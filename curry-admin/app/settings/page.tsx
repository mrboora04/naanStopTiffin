"use client";

import { useState, useEffect } from "react";
import { useAppContext } from "@/contexts/AppContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

export default function SettingsPage() {
  const { token, setToken } = useAppContext();
  const { t } = useLanguage();
  const [localToken, setLocalToken] = useState("");
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    setLocalToken(token);
  }, [token]);

  const handleSave = () => {
    setToken(localToken);
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 3000);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">{t.settings}</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Authentication & API</CardTitle>
          <CardDescription>
            Manage your API tokens and authentication settings for the dashboard.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="token">API Token</Label>
            <Input
              id="token"
              type="password"
              placeholder="Enter your API token..."
              value={localToken}
              onChange={(e) => setLocalToken(e.target.value)}
            />
            <p className="text-sm text-gray-500">
              This token is required to authenticate requests and save data securely.
            </p>
          </div>
          <Button onClick={handleSave} className="w-full sm:w-auto">
            {isSaved ? "Saved!" : t.save}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
