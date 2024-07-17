--[[本脚本需配合自动识别程序使用, 且仅支持全自动武器和半自动武器单点压枪, 支持2, 3, 4倍镜和全部配件]]

-- 补偿 垂直握把1
-- 补偿 半截式握把1.05
-- 补偿 拇指握把1.15
-- 补偿 轻型握把1.15
-- 补偿 无握把1.32

-- 消焰 垂直握把1.08
-- 消焰 半截式握把1.18
-- 消焰 拇指握把1.23
-- 消焰 轻型握把1.23
-- 消焰 无握把1.40

-- 无枪口 垂直握把1.28
-- 无枪口 半截式握把1.32
-- 无枪口 拇指握把1.44
-- 无枪口 轻型握把1.44
-- 无枪口 无握把1.6

-- 测试

-- [[全局动态注入参数 - 使用dofile更新]]
-- 枪械名字, 默认识别为空, 为空时值为"None".
GunName = "None"

-- 后坐力系数, 默认为1即满配(枪口补偿, 拇指握把, 战术枪托, 基础瞄具). 该系数为配件相关系数, 不代表最终系数, 由识别的配件相乘得出.
RecoilFactor = 1

-- 当前人物姿势, 1-站立, 2-蹲下, 3-卧倒. 不同姿势对应不同的后坐力系数
Posture = 1

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
ConfigPath = "C:/Users/Public/Downloads/pubg_config.lua"

--[[枪械参数]]
Guns = {
    m762 = {
        interval = 83,
        standingRecoilFactor = 1,
        crouchingRecoilFactor = 0.83,
        proneRecoilFactor = 0.59,
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

--[[函数定义]]
-- 加载配置
function LoadConfig()
    dofile(ConfigPath)
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

-- 展开折叠后坐力列表
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
EnablePrimaryMouseButtonEvents(true) -- 开启鼠标左键监听
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
            if GunName ~= "None" then
                local gunData = Guns[GunName]
                -- 计算弹道
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
