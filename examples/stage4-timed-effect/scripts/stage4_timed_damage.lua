local TIMER = "stage4_timed_damage"
local TARGET = "stage4_timed_damage_target"
local KEY = "stage4_timed_damage"

local function IsFiniteNumber(value)
    return type(value) == "number" and value > -math.huge and value < math.huge
end

local function GetDamageList(target)
    local combat = target ~= nil and target:IsValid() and target.components.combat
    return combat and combat.externaldamagemultipliers or nil
end

local function InstallTimedDamage(inst)
    local timer = inst:AddComponent("timer")
    local tracker = inst:AddComponent("entitytracker")
    local multiplier
    local applied_target
    local applied_list
    local OnTargetRemoved

    local function StopTimedEffect()
        if applied_target ~= nil then
            inst:RemoveEventCallback("onremove", OnTargetRemoved, applied_target)
            applied_list:RemoveModifier(inst, KEY)
        end
        applied_target = nil
        applied_list = nil
        timer:StopTimer(TIMER)
        tracker:ForgetEntity(TARGET)
        multiplier = nil
    end

    OnTargetRemoved = function(removed)
        if removed == applied_target then
            StopTimedEffect()
        end
    end

    local function Apply(target, list)
        applied_target = target
        applied_list = list
        inst:ListenForEvent("onremove", OnTargetRemoved, target)
        list:SetModifier(inst, multiplier, KEY)
    end

    function inst:StartTimedEffect(target, value, duration)
        if not self:IsValid() or target == self
            or not IsFiniteNumber(value) or value < 0
            or not IsFiniteNumber(duration) or duration <= 0 then
            return false
        end
        local list = GetDamageList(target)
        if list == nil then
            return false
        end
        StopTimedEffect()
        multiplier = value
        tracker:TrackEntity(TARGET, target)
        timer:StartTimer(TIMER, duration)
        Apply(target, list)
        return true
    end

    inst.StopTimedEffect = StopTimedEffect
    inst:ListenForEvent("onremove", StopTimedEffect)
    inst:ListenForEvent("timerdone", function(_, data)
        if data.name == TIMER then
            StopTimedEffect()
        end
    end)

    inst.OnSave = function(_, data)
        data.stage4_damage_multiplier = multiplier
    end

    -- Release any live application before component load can replace its timer.
    inst.OnPreLoad = StopTimedEffect

    inst.OnLoad = function(_, data)
        multiplier = data and data.stage4_damage_multiplier
    end

    inst.OnLoadPostPass = function()
        local target = tracker:GetEntity(TARGET)
        local list = GetDamageList(target)
        local remaining = timer:GetTimeLeft(TIMER)
        if IsFiniteNumber(multiplier) and multiplier >= 0 and list ~= nil
            and IsFiniteNumber(remaining) and remaining > 0 and not timer:IsPaused(TIMER) then
            Apply(target, list)
        else
            StopTimedEffect()
        end
    end
end

return InstallTimedDamage
