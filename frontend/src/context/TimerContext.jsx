import React, { createContext, useContext, useEffect, useState } from "react";

const TimerContext = createContext();

export const TimerProvider = ({ children }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [status, setStatus] = useState("Idle");

  useEffect(() => {
    let interval;

    if (isRunning) {
      interval = setInterval(() => {
        setElapsedTime((prev) => prev + 1);
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [isRunning]);

  const startTimer = () => {
    setElapsedTime(0);
    setStatus("Processing...");
    setIsRunning(true);
  };

  const stopTimer = () => {
    setIsRunning(false);
    setStatus("Completed");
  };

  const resetTimer = () => {
    setElapsedTime(0);
    setStatus("Idle");
    setIsRunning(false);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;

    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  };

  return (
    <TimerContext.Provider
      value={{
        isRunning,
        elapsedTime,
        formattedTime: formatTime(elapsedTime),
        status,
        startTimer,
        stopTimer,
        resetTimer,
      }}
    >
      {children}
    </TimerContext.Provider>
  );
};

export const useTimer = () => useContext(TimerContext);