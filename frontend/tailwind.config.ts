import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        serif: ["'Noto Serif JP'", "serif"],
        sans: ["'Noto Sans JP'", "sans-serif"],
      },
      colors: {
        // 資料館の閲覧室をイメージしたトークン。
        // paper: 紙の地色 / ink: 本文 / pine: 主要な操作色（送信ボタン等）
        // kraft: 出典・メタ情報に使う控えめな差し色 / line: 罫線
        paper: "#FBFAF7",
        ink: "#1E2430",
        pine: "#2F5D50",
        "pine-dark": "#234840",
        kraft: "#8A6D3B",
        line: "#D9D5C9",
      },
    },
  },
  plugins: [],
};

export default config;
