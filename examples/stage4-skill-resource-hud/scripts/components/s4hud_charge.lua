local values = require("s4hud_charge_values")
local MAX, COST = values.MAX, values.COST

local function OnSetOwner(inst)
    local charge = inst.components.s4hud_charge
    if charge ~= nil and charge.classified:IsValid() then
        charge.classified.Network:SetClassifiedTarget(inst)
    end
end

local Charge = Class(function(self, inst)
    self.inst = inst
    local classified = SpawnPrefab("s4hud_charge_classified")
    self.classified = classified
    -- Park delivery until the normal player ownership event.
    classified.Network:SetClassifiedTarget(classified)
    classified.entity:SetParent(inst.entity)
    self:SetCurrent(MAX)

    inst:ListenForEvent("setowner", OnSetOwner)
    local userid = inst.Network:GetUserID()
    if userid ~= nil and userid ~= "" then
        classified.Network:SetClassifiedTarget(inst)
    end
end)

function Charge:GetCurrent()
    return self.current
end

function Charge:SetCurrent(value)
    if type(value) ~= "number" or value ~= value or value == math.huge or value == -math.huge then
        return false
    end
    self.current = math.floor(math.max(0, math.min(MAX, value)))
    self.classified.charge:set(self.current + 1)
    -- The hosting player reads the component directly.
    self.inst:PushEvent("s4hud_charge_changed")
    return true
end

function Charge:TryPulse(act, getcharge)
    if self.casting then
        return false
    elseif self.current < COST then
        return false, "NOCHARGE"
    end

    -- SpawnPrefab can dispatch entity_spawned hooks before it returns.
    self.casting = true
    local fx = SpawnPrefab("small_puff")
    if fx == nil then
        self.casting = nil
        return false
    end

    if not fx:IsValid() or getcharge(act) ~= self or self.current < COST
        or not self.classified:IsValid() then
        if fx:IsValid() then
            fx:Remove()
        end
        self.casting = nil
        return false
    end

    fx.Transform:SetPosition(self.inst.Transform:GetWorldPosition())
    act.s4hud_committed = true
    self.casting = nil
    self:SetCurrent(self.current - COST)
    return true
end

function Charge:OnSave()
    return { current = self.current }
end

function Charge:OnLoad(data)
    if type(data) == "table" then
        self:SetCurrent(data.current)
    end
end

function Charge:OnRemoveEntity()
    self.inst:RemoveEventCallback("setowner", OnSetOwner)
    if self.classified:IsValid() then
        self.classified:Remove()
    end
end

Charge.OnRemoveFromEntity = Charge.OnRemoveEntity

return Charge
