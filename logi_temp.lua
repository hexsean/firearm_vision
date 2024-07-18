GunName = "None"
RecoilFactor = 1
IsRun = false
ClickStartTime = 0
ClickCurrentTime = 0
BulletIndex = 0
XCounter = 0
YCounter = 0
IsDebug = true
AimingModel = 1
CycleDelay = 2
ConfigPath = "C:/Users/Public/Downloads/pubg_config.lua"
Guns = {
    m762 = {
        interval = 86,
        ballistics = {},
        recoilPattern = {
            {1, 37},{2, 25},{3, 32},{4, 34},{5, 37},{6, 39},{7, 44},{8, 46},{9, 46},{10, 45},{11, 47},{12, 45},{13, 49},{19, 55},{42, 20}
        }
    }
}

function LoadConfig()
    dofile(ConfigPath)
    IsRun = true
end

function ResetConfig()
    IsRun = false
    XCounter = 0
    YCounter = 0
    ClickCurrentTime = 0
    SetRandomseed()
end

function SetRandomseed()
    math.randomseed(GetDate("%H%M%S"):reverse())
end

function RandomSleep()
    if IsDebug then
        Sleep(CycleDelay)
    else
        Sleep(math.random(CycleDelay + CycleDelay+5))
    end
end

function FillGaps(recoilPattern)
    local newPattern = {}
    local lastIndex = 0
    for i, pair in ipairs(recoilPattern) do
        local index = pair[1]
        local value = pair[2]
        if index > lastIndex + 1 then
            for j = lastIndex + 1, index - 1 do
                table.insert(newPattern, {j, recoilPattern[i-1][2]})
            end
        end
        table.insert(newPattern, {index, value})
        lastIndex = index
    end
    return newPattern
end

function ExtractValues(recoilPattern)
    local values = {}
    for i, pair in ipairs(recoilPattern) do
        table.insert(values, pair[2])
    end
    return values
end

function math.round(number, decimals)
    local power = 10^decimals
    return math.floor(number * power + 0.5) / power
end

function AccumulateValues(values, coefficient)
    local accumulated = {}
    local sum = 0
    for _, value in ipairs(values) do
        sum = math.round(sum + (value * coefficient), 2)
        table.insert(accumulated, sum)
    end
    return accumulated
end

function ApplyRecoil(gunData, bulletIndex)
    local x = 0
    if IsDebug then
        x = math.ceil((ClickCurrentTime - ClickStartTime) / (gunData.interval * (bulletIndex)) * bulletIndex * 20) - XCounter
    end
    local y = math.ceil((ClickCurrentTime - ClickStartTime) / (gunData.interval * bulletIndex) * gunData.ballistics[bulletIndex]) - YCounter
    MoveMouseRelative(x, y)
    if IsDebug then
        OutputLogMessage("MoveMouseRelative ====> " .. "=== x: " .. x .. " === y: " .. y .. "\n")
    end

    XCounter = XCounter + x
    YCounter = YCounter + y
    RandomSleep()
end

EnablePrimaryMouseButtonEvents(true)

for _, gun in pairs(Guns) do
    gun.recoilPattern = ExtractValues(FillGaps(gun.recoilPattern))
end

function OnEvent (event, arg, family)
    if IsDebug then
        OutputLogMessage("start => " .. "event: " .. event .. " arg: " .. arg .. "\n")
    end

    if event == "MOUSE_BUTTON_PRESSED" and arg == 1 and family == "mouse" then
        ClickStartTime = GetRunningTime()
        Sleep(1)
        if (AimingModel == 1 and IsMouseButtonPressed(3)) or AimingModel == 0 then
            LoadConfig()
            if GunName ~= "None" then
                local gunData = Guns[GunName]
                gunData.ballistics = AccumulateValues(gunData.recoilPattern, RecoilFactor)
                local count = #gunData.ballistics
                while IsMouseButtonPressed(1) do
                    ClickCurrentTime = GetRunningTime()
                    BulletIndex = math.ceil((ClickCurrentTime - ClickStartTime == 0 and 1 or (ClickCurrentTime - ClickStartTime) / gunData.interval))
                    if IsDebug then
                        OutputLogMessage("ApplyRecoil ====> " .. "BulletIndex: " .. BulletIndex .. " ClickCurrentTime: " .. ClickCurrentTime .. " ClickStartTime: " .. ClickStartTime .. " #gunData.ballistics: " .. count .. "\n")
                    end
                    if BulletIndex > count then break end
                    ApplyRecoil(gunData, BulletIndex)
                end
            end
        end
    elseif event == "MOUSE_BUTTON_RELEASED" and arg == 1 and family == "mouse" then
        ResetConfig()
    end
end





