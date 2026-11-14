local values = require("s4hud_charge_values")
local Text = require("widgets/text")

local function ReadCharge(owner)
    local charge = owner.components.s4hud_charge
    if charge ~= nil then
        return charge:GetCurrent()
    end
    local classified = owner._s4hud_classified
    if classified ~= nil and classified:IsValid() then
        local encoded = classified.charge:value()
        if encoded > 0 and encoded <= values.MAX + 1 then
            return encoded - 1
        end
    end
end

return function(AddClassPostConstruct)
    AddClassPostConstruct("widgets/controls", function(controls, owner)
        local text = controls.top_root:AddChild(Text(UIFONT, 28))
        text:SetPosition(0, -72, 0)
        text:SetClickable(false)

        local function Refresh(ghostmode)
            if ghostmode == nil then
                local classified = owner.player_classified
                if classified ~= nil and classified:IsValid() then
                    ghostmode = classified.isghostmode:value()
                else
                    ghostmode = owner:HasTag("playerghost")
                end
            end
            if ghostmode then
                text:Hide()
                return
            end

            local current = ReadCharge(owner)
            text:SetString(current == nil and "Charge: ..." or ("Charge: %d / %d"):format(current, values.MAX))
            text:Show()
        end

        local SetGhostMode = controls.SetGhostMode
        controls.SetGhostMode = function(self, ghostmode, ...)
            SetGhostMode(self, ghostmode, ...)
            Refresh(ghostmode)
        end

        -- The text entity owns the listener. Its removal also removes the subscription.
        text.inst:ListenForEvent("s4hud_charge_changed", function() Refresh() end, owner)
        Refresh()
    end)
end
