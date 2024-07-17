GunName = "None"
RecoilFactor = 1
Posture = 1
IsRun = false
ClickStartTime = 0
ClickCurrentTime = 0
BulletIndex = 0
XCounter = 0
YCounter = 0
IsDebug = false
AimingModel = 1
CycleDelay = 2
ConfigPath = "C:/Users/Public/Downloads/pubg_config.lua"
Guns = {
    m762 = {
        interval = 87,
        standingRecoilFactor = 1,
        crouchingRecoilFactor = 0.83,
        proneRecoilFactor = 0.55,
        ballistics = {},
        recoilPattern = {
            {1, 40},
            {1, 28},
            {1, 19},
            {2, 30},
            {1, 31},
            {1, 32},
            {2, 33},
            {1, 37},
            {9, 38},
            {1, 39},
            {1, 40},
            {1, 40},
            {2, 40},
            {4, 43},
            {7, 45},
            {7, 51}
        }
    },
    aug = {
        interval = 83,
        standingRecoilFactor = 1,
        crouchingRecoilFactor = 0.83,
        proneRecoilFactor = 0.55,
        recoilPattern = {
            {20, 20},
            {20, 30}
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
function ExpandRecoilPattern(recoilPattern)
    local expanded = {}
    for _, pair in ipairs(recoilPattern) do
        local count = pair[1]
        local value = pair[2]
        for i = 1, count do
            table.insert(expanded, value)
        end
    end
    return expanded
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
                local coefficient = 0
                if Posture == 1 then
                	coefficient  = RecoilFactor * gunData.standingRecoilFactor
                elseif Posture == 2 then
                    coefficient  = RecoilFactor * gunData.crouchingRecoilFactor
                elseif Posture == 3 then
                    coefficient  = RecoilFactor * gunData.proneRecoilFactor
                end
                gunData.ballistics = AccumulateValues(ExpandRecoilPattern(gunData.recoilPattern), coefficient)
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
