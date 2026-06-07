import React, { createContext, ReactNode, useMemo } from 'react';
import { useChat } from '@/hooks/useChat';

type ChatContextType = ReturnType<typeof useChat>;

export const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const chat = useChat();
  // Stabilise the context value so non-state consumers (e.g. MessageBubble's
  // `runInTerminal` lookup) don't re-render when an unrelated field changes.
  // We rebuild the object only when one of its fields actually changes.
  const value = useMemo(() => chat, [
    chat.messages,
    chat.isLoading,
    chat.inputText,
    chat.autoExec,
    chat.currentSessionId,
    chat.sessions,
    chat.sessionTitle,
  ]);
  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}
