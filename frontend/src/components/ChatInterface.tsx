import React, { useState, useRef, useEffect } from "react";
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Input,
  Button,
  Avatar,
  Badge,
  IconButton,
  useToast,
} from "@chakra-ui/react";
import { ChatIcon, DeleteIcon } from "@chakra-ui/icons";
import { useMutation, useQuery } from "@tanstack/react-query";
import ChatMessage from "./ChatMessage";
import ThinkingIndicator from "./ThinkingIndicator";
import { chatApi } from "../utils/api";
import { Message, ChatSession } from "../types/chat";

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isThinking, setIsThinking] = useState(false);
  const [thinkingStatus, setThinkingStatus] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const toast = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // System status query
  const { data: systemStatus } = useQuery({
    queryKey: ["systemStatus"],
    queryFn: chatApi.getSystemStatus,
    refetchInterval: (data) => {
      // Stop polling once fully initialized
      return data?.initialized && data?.vector_store ? false : 60000;
    },
  });

  console.log(systemStatus);

  // Start chat mutation
  const startChatMutation = useMutation({
    mutationFn: chatApi.startChat,
    onMutate: () => {
      setIsThinking(true);
      setThinkingStatus("Mr. Munger is beginning to think...");
    },
    onSuccess: (data: ChatSession) => {
      setIsThinking(false);
      setSessionId(data.session_id);

      // Add user message
      const userMessage: Message = {
        id: Date.now().toString(),
        content: inputValue,
        role: "user",
        timestamp: new Date().toISOString(),
      };

      // Add assistant response
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        role: "assistant",
        timestamp: data.timestamp,
        confidence: data.confidence,
        thinkingSteps: data.thinking_steps,
      };

      setMessages([userMessage, assistantMessage]);
      setInputValue("");
    },
    onError: (error: any) => {
      setIsThinking(false);
      toast({
        title: "Error",
        description: error.message || "Failed to start conversation",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    },
  });

  // Continue chat mutation
  const continueChatMutation = useMutation({
    mutationFn: (message: string) => chatApi.continueChat(sessionId!, message),
    onMutate: () => {
      setIsThinking(true);
      setThinkingStatus("Mr. Munger is thinking...");

      // Add user message immediately
      const userMessage: Message = {
        id: Date.now().toString(),
        content: inputValue,
        role: "user",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setInputValue("");
    },
    onSuccess: (data: ChatSession) => {
      setIsThinking(false);

      // Add assistant response
      const assistantMessage: Message = {
        id: Date.now().toString(),
        content: data.response,
        role: "assistant",
        timestamp: data.timestamp,
        confidence: data.confidence,
        thinkingSteps: data.thinking_steps,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    },
    onError: (error: any) => {
      setIsThinking(false);
      toast({
        title: "Error",
        description: error.message || "Failed to continue conversation",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    },
  });

  // Clear session mutation
  const clearSessionMutation = useMutation({
    mutationFn: () => chatApi.clearSession(sessionId!),
    onSuccess: () => {
      setMessages([]);
      setSessionId(null);
      toast({
        title: "Session Cleared",
        description: "Conversation history has been cleared",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to clear session",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    },
  });

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    if (!sessionId) {
      startChatMutation.mutate({ message: inputValue });
    } else {
      continueChatMutation.mutate(inputValue);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleClearSession = () => {
    if (sessionId) {
      clearSessionMutation.mutate();
    }
  };

  const isLoading =
    startChatMutation.isPending || continueChatMutation.isPending;

  return (
    <Box h="100vh" display="flex" flexDirection="column" bg="gray.50">
      {/* Header */}
      <Box
        bg="white"
        borderBottom="1px"
        borderColor="gray.200"
        p={6}
        shadow="sm"
      >
        <VStack spacing={3}>
          <HStack spacing={4} align="center">
            <Avatar
              size="lg"
              name="Charlie Munger"
              src="/Charlie_Munger.jpg"
              bg="gray.600"
            />
            <VStack align="start" spacing={1}>
              <Heading size="lg" color="black" fontFamily="heading">
                The{" "}
                <Text as="span" color="red.400">
                  Munger
                </Text>{" "}
                Talks
              </Heading>
              <Text color="gray.700" fontSize="md" fontFamily="body">
                Chat with Charlie Munger's wisdom and mental models
              </Text>
            </VStack>
          </HStack>

          {/* System Status */}
          <HStack spacing={4} fontSize="sm">
            <Badge
              colorScheme={systemStatus?.initialized ? "green" : "red"}
              variant="solid"
              bg={systemStatus?.initialized ? "green.500" : "red.500"}
            >
              {systemStatus?.initialized ? "System Ready" : "Initializing..."}
            </Badge>
            {systemStatus?.vector_store && (
              <Badge colorScheme="blue" variant="solid" bg="blue.500">
                Knowledge Base: Ready
              </Badge>
            )}
            {systemStatus?.dspy && (
              <Badge colorScheme="purple" variant="solid" bg="purple.500">
                DSPy: Enabled
              </Badge>
            )}
          </HStack>

          {/* Session Info */}
          {sessionId && (
            <HStack spacing={2} fontSize="sm" color="gray.600">
              <Text>Session:</Text>
              <Text fontFamily="mono" color="gray.700">
                {sessionId}
              </Text>
              <IconButton
                aria-label="Clear session"
                icon={<DeleteIcon />}
                size="xs"
                variant="ghost"
                colorScheme="red"
                onClick={handleClearSession}
                isLoading={clearSessionMutation.isPending}
                color="gray.600"
                _hover={{ color: "red.400" }}
              />
            </HStack>
          )}
        </VStack>
      </Box>

      {/* Chat Messages */}
      <Box
        flex="1"
        bg="white"
        overflow="hidden"
        display="flex"
        flexDirection="column"
      >
        <Box flex="1" overflowY="auto" p={4}>
          {messages.length === 0 && !isThinking && (
            <VStack spacing={4} justify="center" h="full" color="gray.700">
              <ChatIcon boxSize={12} />
              <VStack spacing={2} textAlign="center">
                <Text
                  fontSize="lg"
                  fontWeight="semibold"
                  color="black"
                  fontFamily="heading"
                >
                  Welcome to The{" "}
                  <Text as="span" color="red.400">
                    Munger
                  </Text>{" "}
                  Talks
                </Text>
                <Text fontSize="md" color="gray.700" fontFamily="body">
                  Ask Charlie Munger about investing, mental models, business
                  wisdom, or life philosophy.
                </Text>
                <Text fontSize="sm" color="gray.600" fontFamily="body">
                  Example: "What are your thoughts on value investing?" or "Tell
                  me about mental models"
                </Text>
              </VStack>
            </VStack>
          )}

          <VStack spacing={4} align="stretch">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}

            {isThinking && <ThinkingIndicator status={thinkingStatus} />}
          </VStack>

          <div ref={messagesEndRef} />
        </Box>

        {/* Input Area */}
        <Box p={4} borderTop="1px" borderColor="gray.200" bg="white">
          <HStack spacing={3}>
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask Charlie Munger anything..."
              size="lg"
              disabled={isLoading || !systemStatus?.initialized}
              bg="white"
              border="1px"
              borderColor="gray.300"
              color="black"
              fontFamily="body"
              _placeholder={{ color: "gray.500" }}
              _focus={{
                borderColor: "red.400",
                bg: "white",
              }}
            />
            <Button
              onClick={handleSendMessage}
              isLoading={isLoading}
              disabled={!inputValue.trim() || !systemStatus?.initialized}
              colorScheme="red"
              size="lg"
              px={8}
              bg="red.400"
              _hover={{ bg: "red.500" }}
            >
              Send
            </Button>
          </HStack>

          {!systemStatus?.initialized && (
            <Text fontSize="sm" color="orange.500" mt={2} textAlign="center">
              System is initializing... Please wait.
            </Text>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default ChatInterface;
