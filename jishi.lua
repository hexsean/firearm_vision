time1 = 0
time2 = 0

EnablePrimaryMouseButtonEvents(true)
function OnEvent (event, arg, family)
    if event == "MOUSE_BUTTON_PRESSED" and arg == 1 and family == "mouse" then
        time1 = GetRunningTime()
    elseif event == "MOUSE_BUTTON_RELEASED" and arg == 1 and family == "mouse" then
        OutputLogMessage("time ==============> " ..  GetRunningTime()-time1  .. "\n")
    end
end
