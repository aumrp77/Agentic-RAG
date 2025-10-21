import React, { useState } from "react";
import {
  Box,
  HStack,
  VStack,
  Text,
  Avatar,
  Card,
  CardBody,
  Badge,
  Collapse,
  Button,
  Icon,
} from "@chakra-ui/react";
import { ChevronDownIcon, ChevronUpIcon, InfoIcon } from "@chakra-ui/icons";
import ReactMarkdown from "react-markdown";
import { Message, ThinkingStep } from "../types/chat";

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const [showThinking, setShowThinking] = useState(false);
  const isUser = message.role === "user";

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getThinkingStepColor = (status: string) => {
    switch (status) {
      case "thinking":
        return "blue";
      case "planning":
        return "purple";
      case "retrieving":
        return "orange";
      case "synthesizing":
        return "green";
      case "verifying":
        return "yellow";
      case "complete":
        return "teal";
      default:
        return "gray";
    }
  };

  const getThinkingStepIcon = (status: string) => {
    switch (status) {
      case "thinking":
        return "🧠";
      case "planning":
        return "📋";
      case "retrieving":
        return "🔍";
      case "synthesizing":
        return "⚗️";
      case "verifying":
        return "✅";
      case "complete":
        return "🎯";
      default:
        return "💭";
    }
  };

  return (
    <HStack
      align="start"
      spacing={3}
      w="full"
      justify={isUser ? "flex-end" : "flex-start"}
    >
      {!isUser && (
        <Avatar
          size="sm"
          name="Charlie Munger"
          src="/Charlie_Munger.jpg"
          bg="gray.600"
          flexShrink={0}
        />
      )}

      <VStack align={isUser ? "end" : "start"} spacing={2} maxW="80%">
        <Card
          variant={isUser ? "filled" : "outline"}
          bg={isUser ? "red.400" : "white"}
          color={isUser ? "white" : "black"}
          borderColor={isUser ? "red.400" : "gray.200"}
          shadow="sm"
        >
          <CardBody p={4}>
            <Box>
              {isUser ? (
                <Text fontFamily="body">{message.content}</Text>
              ) : (
                <Box className="markdown-content">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </Box>
              )}
            </Box>
          </CardBody>
        </Card>

        {/* Message metadata */}
        <HStack spacing={2} fontSize="xs" color="gray.500">
          <Text>{formatTimestamp(message.timestamp)}</Text>

          {!isUser && message.confidence && (
            <Badge size="sm" colorScheme="green" variant="solid" bg="green.500">
              {Math.round(message.confidence * 100)}% confidence
            </Badge>
          )}

          {!isUser &&
            message.thinkingSteps &&
            message.thinkingSteps.length > 0 && (
              <Button
                size="xs"
                variant="ghost"
                leftIcon={<InfoIcon />}
                onClick={() => setShowThinking(!showThinking)}
                color="gray.500"
                _hover={{ color: "red.400" }}
              >
                {showThinking ? "Hide" : "Show"} thinking process
                <Icon
                  as={showThinking ? ChevronUpIcon : ChevronDownIcon}
                  ml={1}
                />
              </Button>
            )}
        </HStack>

        {/* Thinking process */}
        {!isUser && message.thinkingSteps && (
          <Collapse in={showThinking} animateOpacity>
            <Card
              variant="outline"
              bg="gray.50"
              borderColor="gray.200"
              w="full"
              mt={2}
            >
              <CardBody p={3}>
                <Text
                  fontSize="sm"
                  fontWeight="semibold"
                  mb={3}
                  color="gray.700"
                >
                  Mr. Munger's Thinking Process:
                </Text>
                <VStack spacing={2} align="stretch">
                  {message.thinkingSteps.map(
                    (step: ThinkingStep, index: number) => (
                      <HStack key={index} spacing={3} align="start">
                        <Text fontSize="sm">
                          {getThinkingStepIcon(step.status)}
                        </Text>
                        <VStack align="start" spacing={1} flex="1">
                          <HStack>
                            <Badge
                              size="sm"
                              colorScheme={getThinkingStepColor(step.status)}
                              variant="solid"
                              bg={`${getThinkingStepColor(step.status)}.500`}
                            >
                              {step.status}
                            </Badge>
                            {step.step && (
                              <Text fontSize="xs" color="gray.500">
                                ({step.step})
                              </Text>
                            )}
                          </HStack>
                          <Text fontSize="sm" color="gray.700">
                            {step.message}
                          </Text>
                        </VStack>
                      </HStack>
                    )
                  )}
                </VStack>
              </CardBody>
            </Card>
          </Collapse>
        )}
      </VStack>

      {isUser && <Avatar size="sm" name="You" bg="red.400" flexShrink={0} />}
    </HStack>
  );
};

export default ChatMessage;
