local G = GLOBAL
local values = G.require("s4hud_charge_values")

PrefabFiles = { "s4hud_pulse_stone", "s4hud_charge_classified" }

G.STRINGS.NAMES.S4HUD_PULSE_STONE = "Pulse Stone"
G.STRINGS.RECIPE_DESC.S4HUD_PULSE_STONE = ("Cast a pulse for %d charge."):format(values.COST)
G.STRINGS.CHARACTERS.GENERIC.DESCRIBE.S4HUD_PULSE_STONE = "It feels warm."
G.STRINGS.CHARACTERS.GENERIC.ACTIONFAIL.S4HUD_PULSE = {
    NOCHARGE = "I need more charge.",
}

AddRecipe2("s4hud_pulse_stone", { G.Ingredient("flint", 1) }, G.TECH.NONE, {
    image = "flint.tex",
    atlas = "images/inventoryimages.xml",
})

AddPlayerPostInit(function(inst)
    if G.TheWorld.ismastersim then
        inst:AddComponent("s4hud_charge")
    end
end)

local function GetChargeForCast(act)
    local doer, item = act.doer, act.invobject
    if act.target ~= nil or act:GetActionPoint() ~= nil
        or doer == nil or not doer:IsValid() or not doer:HasTag("player")
        or doer.bufferedaction ~= act
        or doer:HasTag("playerghost") or doer:HasTag("corpse")
        or item == nil or not item:IsValid() or item.prefab ~= "s4hud_pulse_stone" then
        return nil
    end

    local health, inventory = doer.components.health, doer.components.inventory
    local itemcomponent, rider = item.components.inventoryitem, doer.components.rider
    if health == nil or health:IsDead() or inventory == nil
        or inventory:GetActiveItem() ~= nil
        or itemcomponent == nil or itemcomponent.owner ~= doer
        or inventory:GetItemSlot(item) == nil
        or (rider ~= nil and rider:IsRiding()) then
        return nil
    end
    return doer.components.s4hud_charge
end

local pulse = AddAction("S4HUD_PULSE", "Cast Pulse", function(act)
    -- Keep the action failure reason as a separate return value.
    if not G.TheWorld.ismastersim or act.s4hud_committed then
        return false
    end
    local charge = GetChargeForCast(act)
    if charge == nil then
        return false
    end
    return charge:TryPulse(act, GetChargeForCast)
end)
pulse.actionmeter = true

AddComponentAction("INVENTORY", "inventoryitem", function(item, doer, actions)
    if item.prefab == "s4hud_pulse_stone" and doer:HasTag("player")
        and not doer:HasTag("playerghost") and not doer:HasTag("corpse")
        and doer.replica.inventory ~= nil
        and (doer.replica.rider == nil or not doer.replica.rider:IsRiding()) then
        for _, slotitem in pairs(doer.replica.inventory:GetItems()) do
            if item == slotitem then
                table.insert(actions, pulse)
                return
            end
        end
    end
end)

AddStategraphActionHandler("wilson", G.ActionHandler(pulse, "dolongaction"))
AddStategraphActionHandler("wilson_client", G.ActionHandler(pulse, "dolongaction"))

if not G.TheNet:IsDedicated() then
    G.require("s4hud_hud")(AddClassPostConstruct)
end
