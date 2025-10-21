import React from "react";
import ReactDOM from "react-dom/client";
import { ChakraProvider, extendTheme } from "@chakra-ui/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";

const theme = extendTheme({
  config: {
    initialColorMode: "light",
    useSystemColorMode: false,
  },
  colors: {
    brand: {
      50: "#fdfaf4",
      100: "#f7f7f7",
      200: "#e1e1e1",
      300: "#cfcfcf",
      400: "#b1b1b1",
      500: "#9e9e9e",
      600: "#6e6e6e",
      700: "#424242",
      800: "#2d2d2d",
      900: "#1a1a1a",
    },
    gray: {
      50: "#fdfaf4",
      100: "#f7f7f7",
      200: "#e1e1e1",
      300: "#cfcfcf",
      400: "#b1b1b1",
      500: "#9e9e9e",
      600: "#6e6e6e",
      700: "#424242",
      800: "#2d2d2d",
      900: "#1a1a1a",
    },
    red: {
      50: "#fed7d7",
      100: "#feb2b2",
      200: "#fc8181",
      300: "#f56565",
      400: "#df3e3e",
      500: "#c53030",
      600: "#9c2626",
      700: "#742a2a",
      800: "#5c1a1a",
      900: "#3d0f0f",
    },
  },
  fonts: {
    heading: '"Inter", system-ui, "Inter Fallback", sans-serif',
    body: '"Inter", system-ui, "Inter Fallback", sans-serif',
    mono: '"JetBrains Mono", "Fira Code", "Consolas", monospace',
  },
  styles: {
    global: {
      html: {
        fontFamily: '"Inter", system-ui, "Inter Fallback", sans-serif',
      },
      body: {
        bg: "#fdfaf4",
        color: "#000000",
        lineHeight: "1.2",
      },
      p: {
        fontFamily:
          '"Space Grotesk", system-ui, "Space Grotesk Fallback", sans-serif',
      },
    },
  },
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ChakraProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </ChakraProvider>
  </React.StrictMode>
);
