"use client"

import { useChat } from "@ai-sdk/react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MessageCircle, User } from "lucide-react"

export default function SeoulYouthChatbot() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: "/api/chat",
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-green-600 rounded-lg flex items-center justify-center">
              <MessageCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">청년정보통 챗봇</h1>
              <p className="text-sm text-gray-600">서울시 청년 정책을 AI에게 물어보세요</p>
            </div>
          </div>
          <img src="/youth-logo.png" alt="청년정보통 로고" className="h-10 w-auto" />
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6">
        <Card className="h-[600px] flex flex-col">
          <CardHeader className="border-b bg-gradient-to-r from-blue-600 to-green-600 text-white rounded-t-lg">
            <div className="flex items-center gap-3">
              <Avatar className="w-8 h-8">
                <AvatarImage src="/placeholder.svg" />
                <AvatarFallback className="bg-white text-blue-600 text-sm font-bold">AI</AvatarFallback>
              </Avatar>
              <div>
                <h3 className="font-semibold">청년 정책 상담사</h3>
                <p className="text-xs opacity-90">온라인</p>
              </div>
            </div>
          </CardHeader>

          <CardContent className="flex-1 p-0">
            <ScrollArea className="h-full p-4">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center text-gray-600">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">안녕하세요! 👋</h3>
                  <p className="mb-4 max-w-md">
                    서울시 청년 정책, 지원사업, 일자리 정보 등을 AI 상담사에게 물어보세요.
                  </p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {["청년수당", "청년일자리", "주거지원", "창업지원"].map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      {message.role === "assistant" && (
                        <Avatar className="w-8 h-8 mt-1">
                          <AvatarFallback className="bg-blue-100 text-blue-600 text-xs">AI</AvatarFallback>
                        </Avatar>
                      )}
                      <div
                        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                          message.role === "user"
                            ? "bg-blue-600 text-white"
                            : "bg-gray-100 text-gray-900"
                        }`}
                      >
                        {message.content}
                      </div>
                      {message.role === "user" && (
                        <Avatar className="w-8 h-8 mt-1">
                          <AvatarFallback className="bg-green-100 text-green-600 text-xs">
                            <User className="w-4 h-4" />
                          </AvatarFallback>
                        </Avatar>
                      )}
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex gap-3 justify-start">
                      <Avatar className="w-8 h-8 mt-1">
                        <AvatarFallback className="bg-blue-100 text-blue-600 text-xs">AI</AvatarFallback>
                      </Avatar>
                      <div className="bg-gray-100 rounded-2xl px-4 py-3">
                        <span className="text-sm text-gray-500">입력 중...</span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </ScrollArea>
          </CardContent>

          <div className="border-t p-4">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <Input
                value={input}
                onChange={handleInputChange}
                placeholder="질문을 입력하세요..."
                className="flex-1"
                disabled={isLoading}
              />
              <Button type="submit" disabled={isLoading || !input.trim()}>
                전송
              </Button>
            </form>
          </div>
        </Card>
      </div>
    </div>
  )
}