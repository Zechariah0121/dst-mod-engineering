local function NotifyOwner(inst)
    local owner = inst._s4hud_owner
    if owner ~= nil and owner:IsValid() and owner._s4hud_classified == inst then
        owner:PushEvent("s4hud_charge_changed")
    end
end

local function Detach(inst)
    local owner = inst._s4hud_owner
    inst._s4hud_owner = nil
    if owner ~= nil and owner._s4hud_classified == inst then
        owner._s4hud_classified = nil
        if owner:IsValid() then
            owner:PushEvent("s4hud_charge_changed")
        end
    end
end

local function OnEntityReplicated(inst)
    local owner = inst.entity:GetParent()
    if owner ~= nil and owner:IsValid() then
        inst._s4hud_owner = owner
        owner._s4hud_classified = inst
        NotifyOwner(inst)
    end
end

local function fn()
    local inst = CreateEntity()
    if TheWorld.ismastersim then
        inst.entity:AddTransform()
    end
    inst.entity:AddNetwork()
    inst.entity:Hide()
    inst:AddTag("CLASSIFIED")

    -- Zero represents an unavailable snapshot. Stored charge n is encoded as n + 1.
    inst.charge = net_smallbyte(inst.GUID, "s4hud.charge", "s4hud_charge_dirty")
    inst.entity:SetPristine()

    if TheWorld.ismastersim then
        inst.persists = false
    else
        inst.OnEntityReplicated = OnEntityReplicated
        inst.OnRemoveEntity = Detach
        inst:ListenForEvent("s4hud_charge_dirty", NotifyOwner)
    end
    return inst
end

return Prefab("s4hud_charge_classified", fn)
