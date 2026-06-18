"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ShieldCheck,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Upload,
  LogOut,
  User,
} from "lucide-react";

interface CreditAssessment {
  credit_score: number;
  rating: string;
  risk_level: string;
  funding_readiness: string;
}

interface UserData {
  full_name: string;
  email: string;
}

function getScoreColor(score: number) {
  if (score >= 750) return "text-emerald-400";
  if (score >= 700) return "text-blue-400";
  if (score >= 650) return "text-yellow-400";
  return "text-red-400";
}

function getScoreBackground(score: number) {
  if (score >= 750) return "bg-emerald-950/40 border-emerald-900/50";
  if (score >= 700) return "bg-blue-950/40 border-blue-900/50";
  if (score >= 650) return "bg-yellow-950/40 border-yellow-900/50";
  return "bg-red-950/40 border-red-900/50";
}

function getRatingBadgeVariant(rating: string) {
  if (rating === "Excellent" || rating === "Very Good") return "default";
  if (rating === "Good") return "secondary";
  return "destructive";
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserData | null>(() => {
    if (typeof window !== "undefined") {
      const userData = localStorage.getItem("user");
      return userData ? JSON.parse(userData) : null;
    }
    return null;
  });
  const [assessment, setAssessment] = useState<CreditAssessment | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/");
      return;
    }

    const fetchAssessment = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/assessment`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              monthly_income: 500000,
              monthly_expense: 250000,
              existing_loans: 50000,
            }),
          },
        );

        if (res.ok) {
          const data = await res.json();
          setAssessment(data);
        }
      } catch {
        setAssessment({
          credit_score: 780,
          rating: "Very Good",
          risk_level: "Low Risk",
          funding_readiness: "Ready",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchAssessment();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-slate-400 animate-pulse">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <ShieldCheck className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-lg">CrediSure</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-slate-400 text-sm">
              <User className="w-4 h-4" />
              <span>{user?.full_name || "Victor Ugochukwu"}</span>
            </div>
            <Button
              onClick={handleLogout}
              variant="ghost"
              size="sm"
              className="text-slate-400 hover:text-white"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-5xl mx-auto px-6 py-10">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold">
            Welcome back, {user?.full_name?.split(" ")[0] || "Victor"} 👋
          </h1>
          <p className="text-slate-400 mt-1">
            Here is your credit intelligence overview
          </p>
        </div>

        {/* Credit Score Card */}
        {assessment && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
            <Card
              className={`lg:col-span-1 border ${getScoreBackground(assessment.credit_score)}`}
            >
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">
                  Credit Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p
                  className={`text-6xl font-bold ${getScoreColor(assessment.credit_score)}`}
                >
                  {assessment.credit_score}
                </p>
                <p className="text-slate-400 text-sm mt-1">out of 850</p>
                <div className="mt-4">
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className="bg-emerald-500 h-2 rounded-full transition-all"
                      style={{
                        width: `${(assessment.credit_score / 850) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Card className="bg-slate-900 border-slate-800">
                <CardContent className="p-6">
                  <TrendingUp className="w-5 h-5 text-blue-400 mb-3" />
                  <p className="text-slate-400 text-xs mb-1">Risk Rating</p>
                  <p className="text-white font-semibold text-lg">
                    {assessment.rating}
                  </p>
                  <Badge
                    variant={getRatingBadgeVariant(assessment.rating)}
                    className="mt-2 text-xs"
                  >
                    {assessment.rating}
                  </Badge>
                </CardContent>
              </Card>

              <Card className="bg-slate-900 border-slate-800">
                <CardContent className="p-6">
                  <AlertCircle className="w-5 h-5 text-yellow-400 mb-3" />
                  <p className="text-slate-400 text-xs mb-1">Risk Level</p>
                  <p className="text-white font-semibold text-lg">
                    {assessment.risk_level}
                  </p>
                  <Badge variant="secondary" className="mt-2 text-xs">
                    {assessment.risk_level}
                  </Badge>
                </CardContent>
              </Card>

              <Card className="bg-slate-900 border-slate-800">
                <CardContent className="p-6">
                  <CheckCircle className="w-5 h-5 text-emerald-400 mb-3" />
                  <p className="text-slate-400 text-xs mb-1">
                    Funding Readiness
                  </p>
                  <p className="text-white font-semibold text-lg">
                    {assessment.funding_readiness || "Ready"}
                  </p>
                  <Badge className="mt-2 text-xs bg-emerald-700">
                    Eligible
                  </Badge>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-base text-slate-200">
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Button
              onClick={() => router.push("/upload")}
              className="bg-blue-600 hover:bg-blue-500"
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload Bank Statement
            </Button>
            <Button
              variant="outline"
              className="border-slate-700 text-slate-300 hover:text-white"
            >
              Apply for Funding
            </Button>
            <Button
              variant="outline"
              className="border-slate-700 text-slate-300 hover:text-white"
            >
              Complete KYC
            </Button>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
