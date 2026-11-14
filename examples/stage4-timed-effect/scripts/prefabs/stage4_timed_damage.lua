local InstallTimedDamage = require("stage4_timed_damage")

local function Common()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddNetwork()
    inst:AddTag("NOCLICK")
    inst.entity:SetPristine()
    return inst
end

local function Source()
    local inst = Common()
    if TheWorld.ismastersim then
        InstallTimedDamage(inst)
    end
    return inst
end

local function Target()
    local inst = Common()
    if TheWorld.ismastersim then
        inst:AddComponent("combat")
        inst.components.combat:SetDefaultDamage(10)
    end
    return inst
end

return Prefab("stage4_timed_damage_source", Source),
       Prefab("stage4_timed_damage_target", Target)
