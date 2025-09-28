'use client';

import { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { toast } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Scale, 
  Brain, 
  FileText, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Copy,
  ChevronRight,
  Globe,
  Briefcase,
  Settings
} from 'lucide-react';

import { LegalQuestionForm } from '@/components/LegalQuestionForm';
import { LLMResponseCard } from '@/components/LLMResponseCard';
import { ResponseComparison } from '@/components/ResponseComparison';
import { QuestionHistory } from '@/components/QuestionHistory';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { LegalService } from '@/services/legalService';
import { LegalQuestionRequest, LegalQuestionResponse, QuestionHistory as QuestionHistoryType } from '@/types/legal';

export default function HomePage() {
  const [currentResponse, setCurrentResponse] = useState<LegalQuestionResponse | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [selectedQuestionId, setSelectedQuestionId] = useState<string | null>(null);

  // Fetch question history
  const { data: questionHistory, refetch: refetchHistory } = useQuery(
    'questionHistory',
    LegalService.getQuestionHistory,
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  );

  // Ask legal question mutation
  const askQuestionMutation = useMutation(
    LegalService.askLegalQuestion,
    {
      onSuccess: (response) => {
        setCurrentResponse(response);
        toast.success('Legal analysis completed successfully!');
        refetchHistory();
      },
      onError: (error: any) => {
        toast.error(`Error: ${error.response?.data?.detail || error.message}`);
      },
    }
  );

  const handleQuestionSubmit = async (request: LegalQuestionRequest) => {
    try {
      await askQuestionMutation.mutateAsync(request);
    } catch (error) {
      // Error handling is done in the mutation
    }
  };

  const handleHistorySelect = (questionId: string) => {
    setSelectedQuestionId(questionId);
    setShowHistory(false);
  };

  const features = [
    {
      icon: Brain,
      title: 'Multi-LLM Analysis',
      description: 'Get responses from OpenAI GPT-4, Claude 3.5, and Gemini Pro for comprehensive legal insights.'
    },
    {
      icon: Scale,
      title: 'Western & European Law',
      description: 'Specialized knowledge in US, UK, EU, and other major legal jurisdictions.'
    },
    {
      icon: FileText,
      title: 'Response Comparison',
      description: 'Compare and analyze responses from different models to find the best legal guidance.'
    },
    {
      icon: Clock,
      title: 'Fast & Accurate',
      description: 'Get detailed legal analysis in seconds with high accuracy and confidence scoring.'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-indigo-600 rounded-lg">
                <Scale className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Legal Compliance AI</h1>
                <p className="text-sm text-gray-500">Multi-LLM Legal Analysis Platform</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <Clock className="w-4 h-4" />
                <span>History</span>
              </button>
              
              <button className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Hero Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center"
            >
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Get Expert Legal Analysis
              </h2>
              <p className="text-xl text-gray-600 mb-8">
                Ask legal questions and get comprehensive answers from multiple AI models specialized in Western and European law.
              </p>
            </motion.div>

            {/* Question Form */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <LegalQuestionForm
                onSubmit={handleQuestionSubmit}
                isLoading={askQuestionMutation.isLoading}
              />
            </motion.div>

            {/* Current Response */}
            <AnimatePresence>
              {currentResponse && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-6"
                >
                  {/* Response Header */}
                  <div className="bg-white rounded-lg shadow-sm border p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">Legal Analysis Results</h3>
                        <p className="text-sm text-gray-500">
                          Question ID: {currentResponse.question_id}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          currentResponse.confidence_level === 'high' 
                            ? 'bg-green-100 text-green-800'
                            : currentResponse.confidence_level === 'medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {currentResponse.confidence_level.toUpperCase()} CONFIDENCE
                        </span>
                        <span className="text-sm text-gray-500">
                          {currentResponse.processing_time.toFixed(1)}s
                        </span>
                      </div>
                    </div>
                    
                    <div className="text-gray-700">
                      <p className="font-medium mb-2">Question:</p>
                      <p className="text-gray-600 italic">"{currentResponse.question}"</p>
                    </div>
                  </div>

                  {/* LLM Responses */}
                  <div className="space-y-4">
                    {Object.entries(currentResponse.responses).map(([model, response]) => (
                      <LLMResponseCard
                        key={model}
                        model={model}
                        response={response}
                      />
                    ))}
                  </div>

                  {/* Response Comparison */}
                  {currentResponse.comparison && (
                    <ResponseComparison comparison={currentResponse.comparison} />
                  )}

                  {/* Follow-up Suggestions */}
                  {currentResponse.follow_up_suggestions.length > 0 && (
                    <div className="bg-white rounded-lg shadow-sm border p-6">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">
                        Suggested Follow-up Questions
                      </h4>
                      <div className="space-y-2">
                        {currentResponse.follow_up_suggestions.map((suggestion, index) => (
                          <div
                            key={index}
                            className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                            onClick={() => {
                              // Pre-fill the form with this suggestion
                              const form = document.querySelector('textarea[name="question"]') as HTMLTextAreaElement;
                              if (form) {
                                form.value = suggestion;
                                form.focus();
                              }
                            }}
                          >
                            <ChevronRight className="w-4 h-4 text-indigo-600 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-700 text-sm">{suggestion}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Loading State */}
            {askQuestionMutation.isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-white rounded-lg shadow-sm border p-8 text-center"
              >
                <LoadingSpinner size="large" />
                <p className="mt-4 text-gray-600">Analyzing your legal question...</p>
                <p className="text-sm text-gray-500">This may take a few moments as we consult multiple AI models.</p>
              </motion.div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Features */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-lg shadow-sm border p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Features</h3>
              <div className="space-y-4">
                {features.map((feature, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <feature.icon className="w-5 h-5 text-indigo-600" />
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">{feature.title}</h4>
                      <p className="text-xs text-gray-600 mt-1">{feature.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Quick Stats */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-lg shadow-sm border p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Questions</span>
                  <span className="text-sm font-medium text-gray-900">1,250</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Avg Response Time</span>
                  <span className="text-sm font-medium text-gray-900">4.2s</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Success Rate</span>
                  <span className="text-sm font-medium text-green-600">98.5%</span>
                </div>
              </div>
            </motion.div>

            {/* Jurisdictions */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white rounded-lg shadow-sm border p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Supported Jurisdictions</h3>
              <div className="grid grid-cols-2 gap-2">
                {['US', 'UK', 'EU', 'DE', 'FR', 'IT', 'ES', 'CA', 'AU'].map((jurisdiction) => (
                  <div
                    key={jurisdiction}
                    className="flex items-center space-x-2 p-2 bg-gray-50 rounded text-sm"
                  >
                    <Globe className="w-3 h-3 text-indigo-600" />
                    <span className="text-gray-700">{jurisdiction}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Question History Modal */}
      <AnimatePresence>
        {showHistory && (
          <QuestionHistory
            questions={questionHistory || []}
            onSelect={handleHistorySelect}
            onClose={() => setShowHistory(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
