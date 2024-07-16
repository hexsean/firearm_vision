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

CpuLoad = 20

ConfigPath = "C:/Users/Public/Downloads/pubg_config.lua"

Guns = {
    M762 = {
        interval = 86,
        standingRecoilFactor = 1,
        crouchingRecoilFactor = 0.83,
        proneRecoilFactor = 0.55,
        recoilPattern = { 40, 25, 18, 18, 17, 18, 19, 20, 20, 23, 24, 24, 24, 24, 24, 24, 24, 24, 24, 25, 28, 29, 27, 27, 28, 28, 28, 28, 30, 30, 30, 30, 30, 30, 30, 29, 29, 29, 29, 29}
    },
    AUG = {
        interval = 84,
        standingRecoilFactor = 1,
        crouchingRecoilFactor = 0.83,
        proneRecoilFactor = 0.55,
        recoilPattern = { 5, 5, 5, 9, 14, 20, 27, 35, 44, 54, 65, 77, 89, 101, 113, 125, 137, 148, 159, 169, 178, 186, 193, 199, 204, 208, 211, 213, 214, 214 }
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
        Sleep(CpuLoad)
    else
        Sleep(math.random(CpuLoad + CpuLoad+5))
    end
end

function GetRealY (y, recoilFactor, posture)
    return y
end

console = {}
function console.log (str)
    OutputLogMessage(table.print(str) .. "\n")
end

function ApplyRecoil(gunData, recoilFactor, posture, bulletIndex)
    OutputLogMessage("999999999999 ====> " .. "bulletIndex: " .. bulletIndex .. " YCounter: " .. YCounter .. "\n")

    if bulletIndex > YCounter then
        local x = 0
        if IsDebug then
            x = 10
        end
        local y = gunData.recoilPattern[bulletIndex]
        local realY = GetRealY(y, recoilFactor, posture)
        MoveMouseRelative(x, realY)
        OutputLogMessage("uuuuu ====> " .. "xxxxxx: " .. x .. " yyyyyy: " .. realY .. "\n")
        YCounter = YCounter + 1
    end

    RandomSleep()
end

EnablePrimaryMouseButtonEvents(true)
function OnEvent (event, arg, family)
    OutputLogMessage("start => " .. "event: " .. event .. " arg: " .. event .. "\n")
    if event == "MOUSE_BUTTON_PRESSED" and arg == 1 and family == "mouse" and ((AimingModel == 1 and IsMouseButtonPressed(3)) or AimingModel == 0) then
        LoadConfig()
        if GunName ~= "None" then
            ClickStartTime = GetRunningTime()
            local gunData = Guns[GunName]
            while IsMouseButtonPressed(1) do
                ClickCurrentTime = GetRunningTime()
                BulletIndex = math.ceil((ClickCurrentTime - ClickStartTime == 0 and 1 or (ClickCurrentTime - ClickStartTime) / gunData.interval))
                OutputLogMessage("ApplyRecoil ====> " .. "BulletIndex: " .. BulletIndex .. " ClickCurrentTime: " .. ClickCurrentTime .. " ClickStartTime: " .. ClickStartTime .. " #gunData.recoilPattern: " .. #gunData.recoilPattern .. "\n")

                if BulletIndex > #gunData.recoilPattern then break end
                ApplyRecoil(gunData, RecoilFactor, Posture, BulletIndex)
            end
        end
    elseif event == "MOUSE_BUTTON_RELEASED" and arg == 1 and family == "mouse" then
        ResetConfig()
    end
end
