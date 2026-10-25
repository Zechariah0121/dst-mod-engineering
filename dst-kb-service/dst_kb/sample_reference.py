"""Named samples as bounded references; existing admission remains independent."""
import json
import re
from functools import lru_cache
from pathlib import Path

from .intent_scope import query_scope, task_subjects
from .relevance_frames import literal_data_prose, _data_quote_view
from .scope_navigation import ExactSourceReader, ProofError, at, digest, ref_key, triple
from .task_relevance import record_content_context, task_support
from .source_epoch_runtime import active_epoch
from .source_identity import steam_source_version

SCHEMA = 'bounded-named-sample-reference/2'
KNOWLEDGE_ROOT = Path(__file__).resolve().parents[2] / 'knowledge'
_VIEWS = frozenset(('decision', 'reviewer', 'evidence'))
_KINDS = frozenset(('NSF', 'RV', 'EI', 'REC', 'UNK'))
_SAMPLE_WORD = re.compile(r'样例|例证|例子|示例|实例|举例|\b(?:samples?|examples?|illustrations?)\b', re.I)
_NO_EXAMPLES = re.compile(
    r'(?:不(?:要|需要|含|带|提供|允许|返回|展示)|无需|别|禁止|排除)\s*'
    r'(?:任何|任何的|具体|提供|返回|展示|附带|包含)?\s*(?:样例|例证|例子|示例|实例|举例)'
    r'|(?:不|别|不要|无需)举例|(?:样例|例证|例子|示例|实例)\s*都?(?:不需要|不要|无需)'
    r'|\b(?:no|without|exclude|excluding)\s+(?:any\s+)?(?:samples?|examples?|illustrations?)\b'
    r'|\bdo\s+not\s+(?:give|include|show|return|provide)\s+(?:any\s+)?(?:samples?|examples?)\b', re.I)
_IMPLEMENTATION = re.compile(r'实现|实现类|路径|\b(?:implementation|prefab|class|path)s?\b', re.I)
_META = re.compile(r'^\s*(?:[A-Za-z_]\w*(?:[.:]\w+)?\s*(?:的\s*)?)?'
    r'(?:metadata|labels?|titles?|navigation|keywords?|API names|元数据|标签|标题|题名|导航)'
    r'\s*(?:[:：]|是|为|(?:stores?|contains?|lists?|quotes?)\b)', re.I)
_COMMIT = re.compile(r'[a-f0-9]{40}')
_URL = re.compile(r'https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/blob/([a-f0-9]{40})/[^\s#]+(?:#L[0-9]+(?:-L[0-9]+)?)?')


def _identity_match(text, aliases):
    return any(alias in text if re.search(r'[\u3400-\u9fff]', alias) else bool(re.search(
        r'(?<![A-Za-z0-9_])' + re.escape(alias) + r'(?![A-Za-z0-9_])', text, re.I))
        for alias in aliases)


def _original_atom(record, atom):
    if not isinstance(record, dict) or not isinstance(atom, dict):
        return None
    pointer = atom.get('record_pointer')
    if not isinstance(pointer, str) or not re.fullmatch(r'/claims/(0|[1-9][0-9]*)|/native_fact', pointer):
        return None
    try:
        original = at(record, pointer)
    except (ProofError, KeyError, IndexError, TypeError, ValueError):
        return None
    if not isinstance(original, dict):
        return None
    kind = original.get('kind', original.get('claim_type'))
    if (kind not in _KINDS or atom.get('kind') != kind or
            not isinstance(original.get('statement'), str) or not original['statement'].strip() or
            atom.get('statement') != original['statement']):
        return None
    return original


def _scope_refs(scope):
    result = []
    if not isinstance(scope, dict):
        return result
    for name in ('snapshot_source',):
        if isinstance(scope.get(name), dict):
            result.append(scope[name])
    result.extend(row for row in scope.get('scope_refs', []) if isinstance(row, dict))
    result.extend(row['scope_ref'] for row in scope.get('source_scopes', [])
                  if isinstance(row, dict) and isinstance(row.get('scope_ref'), dict))
    return result


def _accepted_catalog():
    context = active_epoch()
    return _accepted_catalog_for(context.root if context is not None else KNOWLEDGE_ROOT,
                                 context.cache_key if context is not None else 'legacy-unbound')


@lru_cache(maxsize=8)
def _accepted_catalog_for(root, epoch_key):
    document = json.loads((Path(root) / 'data/nativecore/native-core.json').read_text(encoding='utf-8'))
    return {row['id']: digest(row) for row in document['entries']}, document['source_artifacts']


_accepted_catalog.cache_clear = _accepted_catalog_for.cache_clear


def _reader(record, original):
    # 准入不接受 JSON 的 verified/proof 标签；默认重新绑定当前 canonical 与登记过的原件。
    accepted, manifest = _accepted_catalog()
    if accepted.get(record.get('id')) != digest(record):
        raise ProofError('SAMPLE_REFERENCE_RECORD_NOT_CANONICAL')
    refs = list(original.get('evidence_refs', [])) + _scope_refs(record.get('scope'))
    context = active_epoch()
    return ExactSourceReader(context.root if context is not None else KNOWLEDGE_ROOT, manifest, refs)


def _node_kind(node):
    values = {node[key] for key in ('kind', 'claim_type') if key in node}
    return next(iter(values)) if len(values) == 1 and values <= _KINDS else None


def _reviewer_fact_version(scope, original, kind, ref, fact, reader):
    """Existing native005 NSF shape, proved only by this claim's exact refs."""
    if (kind != 'NSF' or original.get('kind', original.get('claim_type')) != 'NSF'
            or any(original[key] != 'NSF' for key in ('kind', 'claim_type') if key in original)
            or reader.root_schema(ref) != {'schema_version': 'native005.scoped-ui-complete.v1'}
            or not isinstance(fact, dict) or fact.get('classification') != 'DirectLuaSourceFact'
            or any(fact[key] != 'NSF' for key in ('kind', 'claim_type') if key in fact)
            or not isinstance(fact.get('statement'), str) or not fact['statement'].strip()
            or fact['statement'] != original.get('statement')
            or not isinstance(fact.get('fact_id'), str) or not fact['fact_id'].strip()
            or not isinstance(fact.get('scope'), str) or not fact['scope'].strip()
            or not isinstance(scope.get('original_fact_ids'), list)
            or fact['fact_id'] not in scope['original_fact_ids']
            or not isinstance(scope.get('original_fact_statements'), dict)
            or scope['original_fact_statements'].get(fact['fact_id']) != fact['statement']):
        return None
    own = {ref_key(value): value for value in original.get('evidence_refs', [])}
    if ref_key(ref) not in own or not re.fullmatch(r'/reviewer_facts/(0|[1-9][0-9]*)', ref['pointer']):
        return None
    metadata = {}
    for name in ('source_commit', 'repository'):
        root_ref = {**triple(ref), 'pointer': '/' + name}
        if ref_key(root_ref) not in own:
            return None
        metadata[name] = reader.read(root_ref)
    commit, repository = metadata['source_commit'], metadata['repository']
    snapshot = scope.get('snapshot_id')
    if (not isinstance(commit, str) or not _COMMIT.fullmatch(commit)
            or not isinstance(repository, str) or not repository.strip()
            or commit != scope.get('source_commit') or repository != scope.get('source_repository')
            or not isinstance(snapshot, str) or not snapshot.strip()):
        return None
    snapshot_ref = scope.get('snapshot_source')
    if (ref_key(snapshot_ref) not in own or snapshot_ref['pointer'] != '/snapshot_id'
            or reader.root_schema(snapshot_ref) != {'schema_version': '1.0'}
            or reader.read(snapshot_ref) != snapshot):
        return None

    def same_version(node):
        return all(node[key] == expected
                   for names, expected in ((('snapshot_id', 'source_snapshot_id', 'dot_snapshot_id'), snapshot),
                                           (('source_commit', 'commit', 'dot_source_commit'), commit),
                                           (('source_repository', 'repository'), repository))
                   for key in names if key in node)

    if not same_version(scope) or not same_version(fact):
        return None
    citations = fact.get('citations')
    if not isinstance(citations, list) or not citations:
        return None
    prefix = ref['pointer'] + '/citations/'
    # Reject malformed or cross-artifact siblings instead of filtering them out.
    for key in own:
        if key[2].startswith(prefix):
            index = key[2][len(prefix):]
            if (key[:2] != ref_key(ref)[:2] or not re.fullmatch(r'0|[1-9][0-9]*', index)
                    or int(index) >= len(citations)):
                return None
    for index, citation in enumerate(citations):
        citation_ref = {**triple(ref), 'pointer': prefix + str(index)}
        if (not isinstance(citation, dict) or ref_key(citation_ref) not in own
                or reader.read(citation_ref) != citation or not same_version(citation)):
            return None
        if 'url' in citation:
            url = _URL.fullmatch(citation['url']) if isinstance(citation['url'], str) else None
            if url is None or url[1] != repository or url[2] != commit:
                return None
    # Original fact.scope stays in its SHA-checked whole node. No root Scope API
    # exists here; a copied root Scope never authorizes reading another pointer.
    return {'snapshot_id': snapshot, 'source_commit': commit, 'source_repository': repository,
            'repository_status': 'DISCLOSED', 'original_fact_ref': triple(ref)}


def _fixed_version(record, original, kind, source_reader):
    scope = record.get('scope')
    if not isinstance(scope, dict) or not isinstance(source_reader, ExactSourceReader):
        return None
    refs = original.get('evidence_refs', [])
    facts = []
    schema_facts = []
    schema_read_failed = False
    schema_type_conflict = False
    identities = {}
    for ref in refs:
        try:
            ref_key(ref)
            node = source_reader.read(ref)
        except (ProofError, KeyError, IndexError, TypeError, ValueError, OSError):
            if (isinstance(ref, dict) and isinstance(ref.get('pointer'), str)
                    and re.fullmatch(r'/reviewer_facts/(0|[1-9][0-9]*)', ref['pointer'])):
                schema_read_failed = True
            continue
        if (isinstance(node, dict) and node.get('statement') == original['statement']
                and re.fullmatch(r'/reviewer_facts/(0|[1-9][0-9]*)', ref['pointer'])):
            if any(key in node for key in ('kind', 'claim_type')):
                if any(node[key] != kind for key in ('kind', 'claim_type') if key in node):
                    schema_type_conflict = True
            else:
                schema_facts.append((ref, node))
        if (isinstance(node, dict) and node.get('statement') == original['statement']
                and _node_kind(node) == kind):
            facts.append((ref, node))
    # Literal proofs keep their complete old route, including its failure rules.
    # Only their absence enables the supported-schema adapter; unrelated context
    # refs cannot add a new gate to an existing literal proof.
    if not facts:
        if schema_read_failed or schema_type_conflict:
            return None
        for ref, node in schema_facts:
            try:
                version = _reviewer_fact_version(scope, original, kind, ref, node, source_reader)
            except (ProofError, KeyError, IndexError, TypeError, ValueError, OSError):
                return None
            if version is None:
                return None
            identity = tuple(version[key] for key in ('snapshot_id', 'source_commit', 'source_repository'))
            identities.setdefault(identity, version)
    for ref, fact in facts:
        if isinstance(fact.get('source_scope'), dict) and 'archive_sha256' in fact['source_scope']:
            # Steam evidence has a frozen archive/file authority rather than a
            # Git commit. Require this original fact's exact scope and citations.
            own = {ref_key(value): value for value in refs}
            scope_ref = {**triple(ref), 'pointer': '/source_scope'}
            source_scope = fact['source_scope']
            if (not re.fullmatch(r'/facts/(0|[1-9][0-9]*)', ref['pointer']) or
                    ref_key(scope_ref) not in own or source_reader.read(scope_ref) != source_scope or
                    not any(row.get('scope_ref') == scope_ref and
                            row.get('snapshot_id') == source_scope.get('snapshot_id') and
                            row.get('archive_sha256') == source_scope.get('archive_sha256')
                            for row in scope.get('source_scopes', []) if isinstance(row, dict))):
                return None
            citations = fact.get('citations', [])
            for index, citation in enumerate(citations):
                citation_ref = {**triple(ref), 'pointer': ref['pointer'] + '/citations/' + str(index)}
                if ref_key(citation_ref) not in own or source_reader.read(citation_ref) != citation:
                    return None
            version = steam_source_version(source_scope, citations)
            if version is None:
                return None
            version = {**version, 'repository_status': 'NOT_ASSERTED_FOR_STEAM_ARCHIVE',
                       'original_fact_ref': triple(ref), 'original_source_scope_ref': scope_ref}
            identity = (version['snapshot_id'], version['archive_sha256'], version['steam_buildid'])
            identities.setdefault(identity, version)
            continue
        variants = [scope]
        if isinstance(scope.get('source_scope'), dict):
            source_scope = scope['source_scope']
            # Scope 副本必须与本条原件关联的 exact node 相等，不能由另一个 record 借来版本。
            linked = False
            for own_ref in refs:
                try:
                    if source_reader.read(own_ref) == source_scope:
                        linked = True
                        break
                except (ProofError, KeyError, IndexError, TypeError, ValueError, OSError):
                    continue
            if linked:
                variants.append(source_scope)
        for version in variants:
            snapshot = version.get('snapshot_id', version.get('source_snapshot_id', version.get('dot_snapshot_id')))
            commit = version.get('source_commit', version.get('commit', version.get('dot_source_commit')))
            repository = version.get('source_repository', version.get('repository'))
            snapshot = snapshot if isinstance(snapshot, str) and snapshot.strip() else None
            commit = commit if isinstance(commit, str) and _COMMIT.fullmatch(commit) else None
            if not snapshot and not commit:
                continue
            if snapshot and any(fact[key] != snapshot for key in ('snapshot_id', 'source_snapshot_id') if key in fact):
                return None
            if commit and any(fact[key] != commit for key in ('source_commit', 'commit') if key in fact):
                return None
            repositories, citation_commits = set(), set()
            for citation in fact.get('citations', []):
                if not isinstance(citation, dict):
                    continue
                url = _URL.fullmatch(citation.get('url', ''))
                if url:
                    if commit and url[2] != commit:
                        return None
                    repositories.add(url[1])
                    citation_commits.add(url[2])
            if not commit and len(citation_commits) == 1:
                commit = next(iter(citation_commits))
            elif not commit and len(citation_commits) > 1:
                return None
            if repository:
                if not isinstance(repository, str) or repositories and repositories != {repository}:
                    return None
            elif len(repositories) == 1:
                repository = next(iter(repositories))
            elif len(repositories) > 1:
                return None
            else:
                repository = None
            if repository and any(fact[key] != repository for key in ('source_repository', 'repository') if key in fact):
                return None
            identity = (snapshot, commit, repository)
            identities.setdefault(identity, {'snapshot_id': snapshot, 'source_commit': commit,
                'source_repository': repository, 'repository_status': 'DISCLOSED' if repository else 'UNAVAILABLE_IN_ORIGINAL_SCOPE_AND_CITATIONS',
                'original_fact_ref': triple(ref)})
    return next(iter(identities.values())) if len(identities) == 1 else None


def _sample_sentences(statement, aliases):
    for sentence in re.split(r'[。!?！？\n]|\.\s+', statement):
        sentence = sentence.strip()
        visible = _data_quote_view(sentence, literal_names=False)
        if sentence and not _META.search(sentence) and _identity_match(visible, aliases):
            yield sentence


def _sample_unit_identity(unit, aliases):
    visible = _data_quote_view(unit, literal_names=False)
    for alias in aliases:
        pattern = (re.escape(alias) if re.search(r'[\u3400-\u9fff]', alias) else
                   r'(?<![A-Za-z0-9_])' + re.escape(alias) + r'(?![A-Za-z0-9_])')
        for occurrence in re.finditer(pattern, visible, re.I):
            prefix = visible[:occurrence.start()].strip(' \t,，;；:：')
            if re.fullmatch(r'(?:(?:the|this|that|a|an|selected|original|vanilla)\s+|'
                            r'(?:原版|这个|该|选定|本条|样例|示例|在|从)\s*)*', prefix + (' ' if prefix else ''), re.I):
                return True
    return False


def _local_clauses(sentence):
    visible = _data_quote_view(sentence, literal_names=False)
    pairs, stack, spans, start = {'(': ')', '[': ']', '{': '}', '（': '）'}, [], [], 0
    for index, character in enumerate(visible):
        if character in pairs:
            stack.append(pairs[character])
        elif stack and character == stack[-1]:
            stack.pop()
        elif character in ',，;；' and not stack:
            spans.append((start, index))
            start = index + 1
    if stack:
        return []
    spans.append((start, len(sentence)))
    return [(start, end, sentence[start:end].strip()) for start, end in spans if sentence[start:end].strip()]


def _sample_continuation(clause):
    visible = _data_quote_view(clause, literal_names=False).strip()
    if not visible or _META.search(visible):
        return False
    # 只允许原句的零主语/代词立即接谓词；任意新名字会结构性断开，不能靠 owner 词表猜同一主体。
    return bool(re.match(
        r'(?:(?:只|再|还|并|且|随后|接着|同时|然后|它|其|该回调|此回调)\s*)*'
        r'(?:直接|先|会|又|也)?\s*(?:安装|调用|注册|监听|订阅|读取|清除|清理|移除|撤销|取消|设置|重设|停止|刷新|返回|推送|发送|添加|删除)'
        r'|(?:(?:and|then|also|only)\s+)*(?:(?:it|this callback|the same callback)\s+)?'
        r'(?:registers?|installs?|listens?|subscribes?|reads?|clears?|removes?|cancels?|sets?|stops?|returns?|sends?)\b',
        visible, re.I))


def _local_sample_witness(query, statement, aliases, atom, own_context, request_frames):
    for sentence in _sample_sentences(statement, aliases):
        anchor = None
        for start, end, clause in _local_clauses(sentence):
            direct = _sample_unit_identity(clause, aliases) and not _META.search(clause)
            if direct:
                anchor = (start, clause)
            elif anchor is None or not _sample_continuation(clause):
                anchor = None
                continue
            evidence = sentence[anchor[0]:end]
            local_atom = {**atom, 'statement': evidence}
            local_context = {**own_context, 'original_content_index': record_content_context([local_atom])}
            local = task_support(query, evidence, local_context, request_frames=request_frames)
            unit = local.get('source_unit', '')
            if (local.get('whole_atom_delivery_allowed') and not local.get('subject_mismatch')
                    and isinstance(unit, str) and unit.strip() and unit in evidence):
                return {'source_unit': unit, 'sample_identity_source_unit': anchor[1],
                    'sample_binding': 'SAME_SOURCE_UNIT' if direct else 'LOCAL_SAME_OWNER_CONTINUATION',
                    'task_unit': local.get('task_unit', ''),
                    'relation_frames': local.get('relevance_relation_frames', []),
                    'mechanism_hits': local.get('mechanism_hits', []),
                    'support_meaning': 'TASK_RELEVANCE_ONLY', 'query_assertion_verified': False}
    return None


_PARAGRAPH_NAME = r'[A-Za-z_][A-Za-z0-9_]*(?:[.:][A-Za-z_][A-Za-z0-9_]*)*'
_PARAGRAPH_LINK = re.compile(
    r'^(?:(?:只|再|还|并|且|随后|接着|同时|然后)\s*|(?:and|then|also|only)\s+)*', re.I)
_PARAGRAPH_PRONOUN = re.compile(
    r'^(它|其|该回调|此回调|it\b|this callback\b|the same callback\b)\s*', re.I)
_PARAGRAPH_PATH = re.compile(
    r'(?:' + _PARAGRAPH_NAME + r'\s*(?:路径|分支)|\b' + _PARAGRAPH_NAME + r'\s+(?:path|branch)\b)', re.I)
_PARAGRAPH_NOUN = (
    r'目标|对象|实体|玩家|世界|资源|事件|攻击|输入|引用|回调|监听|订阅|字段|配置|状态|句柄|'
    r'来源|结果|数值|数据|地图|探索|动作|移动|任务|标签|模式|位置|延迟|副本|组件|参数|属性|源')
_PARAGRAPH_OBJECT = (r'(?:' + _PARAGRAPH_NAME + r'|'
    r'(?:(?:当前|本地|选定|原始|相应|同一|这份|该)\s*)?(?:' + _PARAGRAPH_NOUN + r')+)')
_PARAGRAPH_CJK_ACTION = re.compile(
    r'(?:(?:直接|先|会|又|也|只)\s*)*'
    r'(?:(?:在|向|对|从)\s*' + _PARAGRAPH_OBJECT + r'\s*)?'
    r'(?:安装|调用|注册|监听|订阅|读取|清除|清理|移除|撤销|取消|设置|重设|停止|刷新|返回|推送|发送|添加|删除|'
    r'捕获|生成|切换|传送|恢复|进入|发|调)\s*' + _PARAGRAPH_OBJECT, re.I)
_PARAGRAPH_EN_ACTION = re.compile(
    r'(?:(?:directly|first|also|only)\s+)*'
    r'(?:registers?|installs?|listens?|subscribes?|reads?|clears?|removes?|cancels?|sets?|stops?|returns?|'
    r'sends?|captures?|creates?|enters?|restores?)\s+'
    r'(?:' + _PARAGRAPH_NAME + r'|(?:(?:the|its|current|local|selected|original|same)\s+)?'
    r'(?:target|object|entity|player|world|resource|event|attack|input|reference|callback|listener|subscription|'
    r'field|configuration|state|handle|source|result|value|data|action|task|tag|mode|position|component|argument)s?'
    r'(?:\s+(?:reference|event|listener|callback|state|handle|source|result|value|data|action|task|tag|mode)s?)*)', re.I)
_PARAGRAPH_ACTION_JOIN = re.compile(r'\s*(?:并且|随后|接着|然后|并|且|\b(?:and|then)\b)\s*', re.I)


def _paragraph_unambiguous_behavior(visible):
    """Fully consume a small predicate/object grammar; never guess a tail."""
    for index, action in enumerate(_PARAGRAPH_ACTION_JOIN.split(visible.strip())):
        if index:
            pronoun = _PARAGRAPH_PRONOUN.match(action)
            if pronoun:
                action = action[pronoun.end():]
        if not (_PARAGRAPH_CJK_ACTION.fullmatch(action) or _PARAGRAPH_EN_ACTION.fullmatch(action)):
            return False
    return True


def _paragraph_clause_spans(visible):
    """Keep even empty/quote-masked spans so they remain binding barriers."""
    pairs, stack, spans, start = {'(': ')', '[': ']', '{': '}', '（': '）'}, [], [], 0
    for index, character in enumerate(visible):
        if character in pairs:
            stack.append(pairs[character])
        elif stack and character == stack[-1]:
            stack.pop()
        elif character in ',，;；' and not stack:
            spans.append((start, index))
            start = index + 1
    if stack:
        return []
    return spans + [(start, len(visible))]


def _paragraph_actor(clause, owner):
    """Resolve only an explicit same name or a directly bound continuation."""
    visible = _data_quote_view(clause, literal_names=False).strip()
    if not visible or _META.search(visible):
        return None
    visible = _PARAGRAPH_LINK.sub('', visible)
    path_member = re.match(r'(?:该|此|上述|选定的)路径(?:中|内)?的\s*(' +
                           _PARAGRAPH_NAME + r')(?:\(\))?\s*', visible, re.ASCII)
    if path_member and _paragraph_unambiguous_behavior(visible[path_member.end():]):
        return path_member.group(1), 'EXPLICIT_PATH_MEMBER_ACTOR'
    if owner is None:
        return None
    pronoun = _PARAGRAPH_PRONOUN.match(visible)
    if pronoun and _paragraph_unambiguous_behavior(visible[pronoun.end():]):
        return owner, 'UNIQUE_PRONOUN_ANTECEDENT'
    named = re.match(r'(' + _PARAGRAPH_NAME + r')(?:\(\))?\s*', visible, re.ASCII)
    if (named and named.group(1).casefold() == owner.casefold()
            and _paragraph_unambiguous_behavior(visible[named.end():])):
        return owner, 'EXPLICIT_SAME_ACTOR'
    return None


def _paragraph_identity_anchor(clause, aliases):
    """The sample may name a path while its explicitly named owner acts."""
    visible = _data_quote_view(clause, literal_names=False).strip()
    if not visible or _META.search(visible):
        return None
    for alias in aliases:
        identity = re.escape(alias)
        if not re.search(r'[\u3400-\u9fff]', alias):
            identity = r'(?<![A-Za-z0-9_])' + identity + r'(?![A-Za-z0-9_])'
        if re.fullmatch(r'(?:选定|所选|选中的)\s*' + identity + r'\s*路径', visible, re.I):
            return {'actor': None, 'identity_relation': 'EXPLICIT_SELECTED_PATH',
                    'identity_source_unit': clause}
        path = re.match(r'(?:(?:原版|选定|所选|选中的|在)\s*)*' + identity +
            r'\s*(?:路径|分支)(?:中|内)?\s*的\s*(' + _PARAGRAPH_NAME + r')(?:\(\))?\s*', visible, re.I)
        possessive = re.match(identity + r'\s*的\s*(' + _PARAGRAPH_NAME + r')(?:\(\))?\s*', visible, re.I)
        direct = re.match(r'(?:(?:原版|选定|这个|该)\s*)*' + identity + r'\s*', visible, re.I)
        for head, relation in ((path, 'EXPLICIT_NAMED_PATH_OWNER'),
                               (possessive, 'EXPLICIT_NAMED_MEMBER_OWNER'),
                               (direct, 'EXPLICIT_SAMPLE_AS_ACTOR')):
            if head and _paragraph_unambiguous_behavior(visible[head.end():]):
                owner = head.group(1) if relation != 'EXPLICIT_SAMPLE_AS_ACTOR' else alias
                return {'actor': owner, 'identity_relation': relation,
                        'identity_source_unit': clause}
    return None


def _paragraph_sample_witness(query, statement, aliases, atom, own_context, request_frames):
    """Identity-only fallback; no earlier prose enters behavior relevance context.

    This deliberately small grammar fails closed at an unparsed/new owner,
    competing path, quoted-only clause or paragraph break. It neither resolves
    arbitrary natural-language coreference nor supplies a missing task domain.
    """
    # Trusted semantic aliases may only tighten this new fallback's negative
    # implementation exclusions. They never enter relevance, actor or Source
    # evidence, and opaque identifier substrings do not create a category.
    if aliases and sample_reference_excluded(query,
            {'identity': aliases[0], 'aliases': aliases}, ' '.join(aliases)):
        return None
    # Mask quotes once before discovering any boundaries: a quoted full stop
    # cannot discard the opening quote or turn later payload into source prose.
    visible_statement = _data_quote_view(statement, literal_names=False, apostrophes_are_quotes=True)
    for paragraph_match in re.finditer(r'[^\r\n]+', visible_statement):
        anchor = None
        paragraph = paragraph_match.group()
        sentence_start = 0
        for boundary in re.finditer(r'[。!?！？]|\.\s+|$', paragraph):
            sentence_end = boundary.start()
            visible_sentence = paragraph[sentence_start:sentence_end]
            original_start = paragraph_match.start() + sentence_start
            original_sentence = statement[original_start:paragraph_match.start() + sentence_end]
            sentence_start = boundary.end()
            clauses = _paragraph_clause_spans(visible_sentence)
            if not clauses:
                anchor = None
                continue
            for clause_start, clause_end in clauses:
                clause = original_sentence[clause_start:clause_end].strip()
                visible_clause = visible_sentence[clause_start:clause_end].strip()
                if (not visible_clause or _data_quote_view(clause, literal_names=False,
                        apostrophes_are_quotes=True) != clause):
                    anchor = None
                    continue
                new_anchor = _paragraph_identity_anchor(clause, aliases)
                if new_anchor:
                    # A later alternate named path cannot retroactively lend
                    # identity to this behavior; it must establish its own head.
                    paths = _PARAGRAPH_PATH.findall(_data_quote_view(clause, literal_names=False))
                    anchor = new_anchor if len(paths) <= 1 else None
                    continue
                if anchor is None:
                    continue
                visible = _data_quote_view(clause, literal_names=False)
                if _PARAGRAPH_PATH.search(visible) or _identity_match(visible, aliases):
                    anchor = None
                    continue
                actor = _paragraph_actor(clause, anchor['actor'])
                if actor is None:
                    anchor = None
                    continue
                if actor[1] == 'EXPLICIT_PATH_MEMBER_ACTOR':
                    # The reference itself names the actor; the sample/path
                    # name is never substituted for that actor.
                    anchor = {**anchor, 'actor': actor[0]}
                behavior_atom = {**atom, 'statement': clause}
                behavior_context = {**own_context,
                    'original_content_index': record_content_context([behavior_atom])}
                support = task_support(query, clause, behavior_context, request_frames=request_frames)
                unit = support.get('relevance_source_unit', support.get('source_unit', ''))
                if (support.get('whole_atom_delivery_allowed') and not support.get('subject_mismatch')
                        and isinstance(unit, str) and unit.strip() and unit in clause):
                    return {'source_unit': unit,
                        'sample_identity_source_unit': anchor['identity_source_unit'],
                        'sample_binding': 'SAME_ORIGINAL_PARAGRAPH_UNIQUE_ACTOR',
                        'sample_identity_relation': anchor['identity_relation'],
                        'behavior_actor': actor[0], 'behavior_actor_binding': actor[1],
                        'behavior_context_source_unit': clause,
                        'identity_record_pointer': atom['record_pointer'],
                        'task_unit': support.get('task_unit', ''),
                        'relation_frames': support.get('relevance_relation_frames', []),
                        'mechanism_hits': support.get('mechanism_hits', []),
                        'support_meaning': 'TASK_RELEVANCE_ONLY', 'query_assertion_verified': False}
    return None


def _excluded(scope, aliases, statement):
    for clause in scope['negative_clauses']:
        if _SAMPLE_WORD.search(clause) or _identity_match(clause, aliases):
            return True
        if _IMPLEMENTATION.search(clause) and task_subjects(clause) & task_subjects(statement):
            return True
    return False


def sample_reference_excluded(query, sample_rule, statement):
    """Explicit exclusions only; this never creates positive sample admission."""
    if not isinstance(query, str):
        return False
    aliases = []
    if isinstance(sample_rule, dict):
        identity = sample_rule.get('identity')
        if isinstance(identity, str) and identity:
            aliases.append(identity)
        if isinstance(sample_rule.get('aliases'), list):
            aliases.extend(value for value in sample_rule['aliases'] if isinstance(value, str) and value)
    statement = statement if isinstance(statement, str) else ''
    # 原 query_scope 会把“不要 buff 实现”拆为 negative=buff、positive=实现；
    # 只在原查询明确否定实现类、且本条原文拥有同一主体时补回该排除。
    visible_query = _data_quote_view(query, literal_names=False)
    for clause in re.split(r'[，,；;。!?！？\n]', visible_query):
        if (re.match(r'\s*(?:不要|排除|无需|忽略|不(?:需要|使用|采用|包含|涉及|讨论|考虑)|'
                     r'without\b|exclud(?:e|ing)\b|no\b|not(?!\s+only\b)\b)', clause, re.I)
                and _IMPLEMENTATION.search(clause)
                and task_subjects(clause) & task_subjects(statement)):
            return True
    return bool(_NO_EXAMPLES.search(literal_data_prose(query, preserved=aliases, literal_names=False)) or
                _excluded(query_scope(query), aliases, statement))


def bounded_sample_reference(record, atom, sample_rule, query, *, context=None,
                             projection='coding', view=None, role='reviewer',
                             existing_admitted=False, existing_deep_admitted=False,
                             request_frames=None, source_reader=None):
    """Return compact disclosure or None for the new unqualified path only.

    The caller supplies an independent existing admission decision. A reader is
    an accepted ExactSourceReader capability, never a JSON proof dictionary.
    Exact browse and explicit positive identity requests remain old-policy work.
    """
    if (projection != 'reviewer' or view not in _VIEWS or role != 'reviewer'
            or existing_admitted is not True or not isinstance(query, str) or not query.strip()):
        return None
    if not isinstance(sample_rule, dict) or not isinstance(sample_rule.get('identity'), str) or not sample_rule['identity']:
        return None
    aliases = sample_rule.get('aliases', [])
    if not isinstance(aliases, list) or not aliases or any(not isinstance(value, str) or not value for value in aliases):
        return None
    aliases = list(dict.fromkeys([sample_rule['identity']] + aliases))
    original = _original_atom(record, atom)
    if original is None or not isinstance(record.get('id'), str):
        return None
    scope = query_scope(query)
    if (_identity_match(scope['positive_user_query'], aliases) or
            sample_reference_excluded(query, sample_rule, atom['statement'])):
        return None
    if (record.get('retrieval_status') in ('restricted',) or record.get('knowledge_status') == 'superseded'
            or (record.get('retrieval_status') == 'deep_only' and
                (existing_deep_admitted is not True or scope['deep_forbidden']))):
        return None
    if context is not None and (not isinstance(context, dict) or
            context.get('record_pointer', atom['record_pointer']) != atom['record_pointer'] or
            context.get('atom_kind', atom['kind']) != atom['kind']):
        return None
    # 本条原句独立重算；传入的标题、receiver、另一句 index 或 proof 标签不提供事实/相关性。
    own_context = {'scope': '', 'receivers': [], 'role_bindings': [],
        'atom_kind': atom['kind'], 'record_pointer': atom['record_pointer'],
        'original_content_index': record_content_context([atom])}
    support = task_support(query, atom['statement'], own_context, request_frames=request_frames)
    if not support.get('whole_atom_delivery_allowed') or support.get('subject_mismatch'):
        return None
    witness = _local_sample_witness(query, atom['statement'], aliases, atom, own_context, request_frames)
    if witness is None:
        witness = _paragraph_sample_witness(query, atom['statement'], aliases, atom, own_context, request_frames)
    if witness is None:
        return None
    try:
        if source_reader is None:
            source_reader = _reader(record, original)
        if not isinstance(source_reader, ExactSourceReader):
            return None
        version = _fixed_version(record, original, atom['kind'], source_reader)
    except (ProofError, KeyError, IndexError, TypeError, ValueError, OSError, UnicodeError):
        return None
    if version is None:
        return None
    return {'schema': SCHEMA, 'sample_identity': sample_rule['identity'],
        'record_id': record['id'], 'record_pointer': atom['record_pointer'], 'kind': atom['kind'],
        'statement_sha256': digest(atom['statement']), 'fixed_source_version': version,
        'current_task_relation': witness, 'reference_only': True,
        'generic_contract_complete': False, 'full_method_contract_verified': False,
        'original_scope_ref': {'record_pointer': '/scope', 'value_sha256': digest(record.get('scope'))},
        'proves': {'record_pointer': atom['record_pointer'], 'kind': atom['kind'],
                   'statement_sha256': digest(atom['statement'])},
        'notice': '具名例证“' + sample_rule['identity'] + '”仅按本条原 atom 的原始类型与证据角色，在固定来源版本及原 Scope 内提供有界参考；'
                  '与当前任务的关联见原句见证。它不证明通用契约完整、被调用方法的完整合同或当前安装版/运行时等价；'
                  '通用知识缺口与原有未知、纠正和适用限制仍须独立保留。'}
