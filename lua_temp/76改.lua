--[[本脚本需配合自动识别程序使用]]

muzzles = "None"
grips = "None"
scopes = "None"
stocks = "None"
poses = "None"

-- [[全局动态注入参数 - 使用dofile更新]]
-- 枪械名字, 默认识别为空, 为空时值为"None".
weapon_name = "None"

-- 枪械名字, 默认识别为空, 为空时值为"None".
bag = "None"

-- 后坐力系数
RecoilCoefficient = 1

--[[全局动态参数 - 脚本运行时更新]]

-- 是否运行脚本, 由当前按键状态决定, 用于中断脚本
IsRun = false

-- 鼠标按下时记录脚本运行时间戳
ClickStartTime = 0

-- 当前时间戳
ClickCurrentTime = 0

-- 第几颗子弹
BulletIndex = 0

XCounter = 0
YCounter = 0

--[[全局静态参数]]

-- 是否开启debug
IsDebug = false

-- 瞄准模式: 0-切换开镜, 1-长按开镜
AimingModel = 1

-- 循环延迟, 值越大循环的频率越低, 屏幕抖动越厉害
CycleDelay = 2

-- 识别程序输出的脚本文件路径
ConfigPath = "改成识别程序的输出路径"

--[[枪械参数]]
Guns = {
    m762 = {
        interval = 86,
        ballistics = {},
        poses = {
            None = 1,
            stand = 1,
            down = 0.81,
        },
        muzzles = {
            None = 1,
            xy1 = 0.86,
            xy2 = 1,
            xy3 = 1,
            bc1 = 0.79,
            bc2 = 1,
            bc3 = 1,
            xx = 1,
            xx1 = 1,
        },
        grips = {
            None = 1,
            angle = 1,
            light = 1,
            red = 1,
            line = 0.86,
            thumb = 1,
        },
        scopes = {
            None = 1,
            reddot = 1,
            quanxi = 1,
            x2 = 1.27,
            x3 = 1.73,
            x4 = 2.565,
            x6 = 1.76,
            x8 = 1,
        },
        stocks = {
            None = 1,
            normal = 1,
            heavy = 1,
            pg = 1,
        },
        recoilPattern = {
            {1, 37},{2, 25},{3, 32},{4, 34},{5, 37},{6, 38},{7, 42},{8, 44},{9, 44},{10, 45},{11, 47},{12, 45},{13, 49},{14, 47},{19, 55},{26, 53},{32, 50},{42, 20}
        }
    }
}

--[[函数定义]]
function CalculationCoefficient()
    local weapon_coefficient = Guns[weapon_name]
    RecoilCoefficient = weapon_coefficient["poses"][poses] * weapon_coefficient["muzzles"][muzzles] * weapon_coefficient["grips"][grips] * weapon_coefficient["scopes"][scopes] * weapon_coefficient["stocks"][stocks]
end


-- 加载配置
function LoadConfig()
    dofile(ConfigPath)
    OutputLogMessage("weapon_name ====> " .. weapon_name .. "\n")
    CalculationCoefficient()
    IsRun = true
end

-- 重置配置
function ResetConfig()
    IsRun = false
    XCounter = 0
    YCounter = 0
    ClickCurrentTime = 0
    SetRandomseed()
end

-- 更新随机数种子(reverse确保变化范围)
function SetRandomseed()
    math.randomseed(GetDate("%H%M%S"):reverse())
end

-- 随机睡眠
function RandomSleep()
    if IsDebug then
        Sleep(CycleDelay)
    else
        Sleep(math.random(CycleDelay + CycleDelay+5))
    end
end

-- 填充后坐力列表
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

-- 去除子弹坐标
function ExtractValues(recoilPattern)
    local values = {}
    for i, pair in ipairs(recoilPattern) do
        table.insert(values, pair[2])
    end
    return values
end

-- 随机数
function math.round(number, decimals)
    local power = 10^decimals
    return math.floor(number * power + 0.5) / power
end

-- 转换至后坐力序列
function AccumulateValues(values, coefficient)
    local accumulated = {}
    local sum = 0
    for _, value in ipairs(values) do
        sum = math.round(sum + (value * coefficient), 2)
        table.insert(accumulated, sum)
    end
    return accumulated
end


-- 压枪
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

--[[开启鼠标监听]]
EnablePrimaryMouseButtonEvents(true)

--[[预处理]]
for _, gun in pairs(Guns) do
    gun.recoilPattern = ExtractValues(FillGaps(gun.recoilPattern))
end

function OnEvent (event, arg, family)
    if IsDebug then
    	OutputLogMessage("start => " .. "event: " .. event .. " arg: " .. arg .. "\n")
    end
    -- 按下鼠标左键, 加载配置项目 (AimingModel == 0时, 仅需按下左键, AimingModel == 1时, 需保持右键按下状态)
    if event == "MOUSE_BUTTON_PRESSED" and arg == 1 and family == "mouse" then
        -- 记录脚本开启时间
        ClickStartTime = GetRunningTime()
        Sleep(1)
        if (AimingModel == 1 and IsMouseButtonPressed(3)) or AimingModel == 0 then
            LoadConfig()
            if weapon_name ~= "None" and bag ~= "bag" then
                local gunData = Guns[weapon_name]
                -- 计算弹道
                gunData.ballistics = AccumulateValues(gunData.recoilPattern, RecoilCoefficient)
                local count = #gunData.ballistics
                while IsMouseButtonPressed(1) do
                    -- 记录当前时间
                    ClickCurrentTime = GetRunningTime()
                    -- 计算当前是第几颗子弹
                    BulletIndex = math.ceil((ClickCurrentTime - ClickStartTime == 0 and 1 or (ClickCurrentTime - ClickStartTime) / gunData.interval))
                    if IsDebug then
                    	OutputLogMessage("ApplyRecoil ====> " .. "BulletIndex: " .. BulletIndex .. " ClickCurrentTime: " .. ClickCurrentTime .. " ClickStartTime: " .. ClickStartTime .. " #gunData.ballistics: " .. count .. "\n")
                    end
                    -- 当前子弹序号不能超过最大值
                    if BulletIndex > count then break end
                    ApplyRecoil(gunData, BulletIndex)
                end
            end
        end
    -- 松开鼠标左键, 恢复动态参数默认值
    elseif event == "MOUSE_BUTTON_RELEASED" and arg == 1 and family == "mouse" then
        ResetConfig()
    end
end
