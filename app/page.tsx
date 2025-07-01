"use client"

import { useChat } from "@ai-sdk/react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Send,
  MessageCircle,
  User,
  Bot,
  Sparkles,
  MapPin,
  Calendar,
  Briefcase,
  GraduationCap,
  Heart,
  Home,
} from "lucide-react"
import { useState } from "react"

const quickActions = [
  { icon: Briefcase, label: "일자리 정보", color: "bg-blue-500" },
  { icon: GraduationCap, label: "교육 프로그램", color: "bg-green-500" },
  { icon: Heart, label: "복지 혜택", color: "bg-pink-500" },
  { icon: Home, label: "주거 지원", color: "bg-purple-500" },
  { icon: Calendar, label: "행사 일정", color: "bg-orange-500" },
  { icon: MapPin, label: "시설 안내", color: "bg-teal-500" },
]

export default function SeoulYouthChatbot() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: "/api/chat",
  })
  const [selectedAction, setSelectedAction] = useState<string | null>(null)

  const handleQuickAction = (action: string) => {
    setSelectedAction(action)
    // 빠른 액션 클릭 시 해당 질문을 자동으로 입력
    const actionQuestions: { [key: string]: string } = {
      "일자리 정보": "청년 일자리 지원 사업에 대해 알려주세요",
      "교육 프로그램": "청년 대상 교육 프로그램이 있나요?",
      "복지 혜택": "청년이 받을 수 있는 복지 혜택을 알려주세요",
      "주거 지원": "청년 주거 지원 정책에 대해 설명해주세요",
      "행사 일정": "이번 달 청년 대상 행사가 있나요?",
      "시설 안내": "청년 이용 가능한 시설을 안내해주세요",
    }

    // 자동으로 질문 제출
    const question = actionQuestions[action]
    if (question) {
      handleSubmit(new Event("submit") as any, { data: { prompt: question } })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            {/* 청년몽땅정보통 로고 추가 */}
            <img src="/youth-logo.png" alt="청년몽땅정보통" className="h-8 w-auto" />
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-green-600 rounded-lg flex items-center justify-center">
              <MessageCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">서울시 청년포털 챗봇</h1>
              <p className="text-sm text-gray-600">청년 정책과 지원사업을 쉽게 찾아보세요</p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Quick Actions Sidebar */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-yellow-500" />
                  빠른 질문
                </h3>
              </CardHeader>
              <CardContent className="space-y-2">
                {quickActions.map((action, index) => (
                  <Button
                    key={index}
                    variant="ghost"
                    className="w-full justify-start gap-3 h-auto p-3 hover:bg-gray-50"
                    onClick={() => handleQuickAction(action.label)}
                  >
                    <div className={`w-8 h-8 rounded-lg ${action.color} flex items-center justify-center`}>
                      <action.icon className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-sm font-medium">{action.label}</span>
                  </Button>
                ))}
              </CardContent>
            </Card>

            {/* Info Card */}
            <Card className="mt-4">
              <CardContent className="p-4">
                <div className="text-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Bot className="w-6 h-6 text-blue-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">AI 청년 도우미</h4>
                  <p className="text-xs text-gray-600 leading-relaxed">
                    서울시 청년 정책, 지원사업, 일자리 정보 등을 실시간으로 안내해드립니다.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-3">
            <Card className="h-[600px] flex flex-col">
              <CardHeader className="border-b bg-gradient-to-r from-blue-600 to-green-600 text-white rounded-t-lg">
                <div className="flex items-center gap-3">
                  <Avatar className="w-8 h-8">
                    <AvatarImage src="/placeholder.svg?height=32&width=32" />
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
                    <div className="flex flex-col items-center justify-center h-full text-center">
                      <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                        <MessageCircle className="w-8 h-8 text-blue-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">안녕하세요! 👋</h3>
                      <p className="text-gray-600 mb-4 max-w-md">
                        서울시 청년포털 AI 상담사입니다. 청년 정책, 지원사업, 일자리 정보 등 궁금한 것을 물어보세요!
                      </p>
                      <div className="flex flex-wrap gap-2 justify-center">
                        <Badge variant="secondary" className="text-xs">
                          청년수당
                        </Badge>
                        <Badge variant="secondary" className="text-xs">
                          청년일자리
                        </Badge>
                        <Badge variant="secondary" className="text-xs">
                          주거지원
                        </Badge>
                        <Badge variant="secondary" className="text-xs">
                          창업지원
                        </Badge>
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
                            className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                              message.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
                            }`}
                          >
                            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
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
                            <div className="flex gap-1">
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                              <div
                                className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                style={{ animationDelay: "0.1s" }}
                              ></div>
                              <div
                                className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                style={{ animationDelay: "0.2s" }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>

              {/* Input Area */}
              <div className="border-t p-4">
                <form onSubmit={handleSubmit} className="flex gap-2">
                  <Input
                    value={input}
                    onChange={handleInputChange}
                    placeholder="청년 정책에 대해 궁금한 것을 물어보세요..."
                    className="flex-1 rounded-full border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                    disabled={isLoading}
                  />
                  <Button
                    type="submit"
                    size="icon"
                    className="rounded-full bg-blue-600 hover:bg-blue-700"
                    disabled={isLoading || !input.trim()}
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </form>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  AI가 생성한 정보는 참고용이며, 정확한 정보는 공식 홈페이지를 확인해주세요.
                </p>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
