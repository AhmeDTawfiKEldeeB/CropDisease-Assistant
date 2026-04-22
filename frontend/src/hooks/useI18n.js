import { createContext, createElement, useContext, useMemo } from "react";

const I18nContext = createContext(null);

export function I18nProvider({ children, value }) {
  const memo = useMemo(() => value, [value]);
  return createElement(I18nContext.Provider, { value: memo }, children);
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used inside I18nProvider");
  }
  return context;
}