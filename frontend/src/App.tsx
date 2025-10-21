import { Box } from "@chakra-ui/react";
import ChatInterface from "./components/ChatInterface";

function App() {
  return (
    <Box minH="100vh" bg="gray.50" color="black">
      <ChatInterface />
    </Box>
  );
}

export default App;
