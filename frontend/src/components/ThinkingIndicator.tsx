import React from "react";
import {
  Box,
  HStack,
  VStack,
  Text,
  Avatar,
  Card,
  CardBody,
  Spinner,
} from "@chakra-ui/react";
import { keyframes } from "@emotion/react";

interface ThinkingIndicatorProps {
  status: string;
}

const pulseAnimation = keyframes`
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
`;

const ThinkingIndicator: React.FC<ThinkingIndicatorProps> = ({ status }) => {
  return (
    <HStack align="start" spacing={3} w="full">
      <Avatar
        size="sm"
        name="Charlie Munger"
        src="/Charlie_Munger.jpg"
        bg="gray.600"
        flexShrink={0}
      />

      <Card variant="outline" bg="white" borderColor="gray.200" maxW="80%">
        <CardBody p={4}>
          <HStack spacing={3} align="center">
            <Spinner size="sm" color="red.400" thickness="2px" />
            <VStack align="start" spacing={1}>
              <Text
                fontSize="sm"
                fontWeight="medium"
                color="red.500"
                fontFamily="body"
              >
                {status}
              </Text>
              <HStack spacing={1}>
                <Box
                  w={2}
                  h={2}
                  bg="red.400"
                  borderRadius="full"
                  animation={`${pulseAnimation} 1.5s ease-in-out infinite`}
                />
                <Box
                  w={2}
                  h={2}
                  bg="red.400"
                  borderRadius="full"
                  animation={`${pulseAnimation} 1.5s ease-in-out infinite 0.2s`}
                />
                <Box
                  w={2}
                  h={2}
                  bg="red.400"
                  borderRadius="full"
                  animation={`${pulseAnimation} 1.5s ease-in-out infinite 0.4s`}
                />
              </HStack>
            </VStack>
          </HStack>
        </CardBody>
      </Card>
    </HStack>
  );
};

export default ThinkingIndicator;
