'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion } from 'framer-motion';
import { z } from 'zod';
import { 
  Send, 
  FileText, 
  Globe, 
  Briefcase, 
  AlertCircle,
  CheckCircle,
  Loader2
} from 'lucide-react';

import { LegalQuestionRequest } from '@/types/legal';

// Form validation schema
const legalQuestionSchema = z.object({
  question: z.string()
    .min(10, 'Question must be at least 10 characters long')
    .max(2000, 'Question must be less than 2000 characters'),
  jurisdiction: z.string().min(1, 'Please select a jurisdiction'),
  practice_area: z.string().min(1, 'Please select a practice area'),
  context: z.string().max(1000, 'Context must be less than 1000 characters').optional(),
  models: z.array(z.string()).optional(),
  include_comparison: z.boolean().default(true),
});

type LegalQuestionFormData = z.infer<typeof legalQuestionSchema>;

interface LegalQuestionFormProps {
  onSubmit: (data: LegalQuestionRequest) => Promise<void>;
  isLoading: boolean;
}

const jurisdictions = [
  { value: 'US', label: 'United States', flag: '🇺🇸' },
  { value: 'UK', label: 'United Kingdom', flag: '🇬🇧' },
  { value: 'EU', label: 'European Union', flag: '🇪🇺' },
  { value: 'DE', label: 'Germany', flag: '🇩🇪' },
  { value: 'FR', label: 'France', flag: '🇫🇷' },
  { value: 'IT', label: 'Italy', flag: '🇮🇹' },
  { value: 'ES', label: 'Spain', flag: '🇪🇸' },
  { value: 'CA', label: 'Canada', flag: '🇨🇦' },
  { value: 'AU', label: 'Australia', flag: '🇦🇺' },
];

const practiceAreas = [
  { value: 'general', label: 'General Law', icon: '⚖️' },
  { value: 'contract', label: 'Contract Law', icon: '📋' },
  { value: 'tort', label: 'Tort Law', icon: '🚨' },
  { value: 'criminal', label: 'Criminal Law', icon: '🔒' },
  { value: 'corporate', label: 'Corporate Law', icon: '🏢' },
  { value: 'employment', label: 'Employment Law', icon: '👥' },
  { value: 'intellectual_property', label: 'Intellectual Property', icon: '💡' },
  { value: 'real_estate', label: 'Real Estate Law', icon: '🏠' },
  { value: 'family', label: 'Family Law', icon: '👨‍👩‍👧‍👦' },
  { value: 'immigration', label: 'Immigration Law', icon: '✈️' },
  { value: 'tax', label: 'Tax Law', icon: '💰' },
  { value: 'regulatory', label: 'Regulatory Law', icon: '📊' },
];

const availableModels = [
  { 
    value: 'gpt-4-turbo-preview', 
    label: 'GPT-4 Turbo', 
    provider: 'OpenAI',
    description: 'Most advanced OpenAI model'
  },
  { 
    value: 'claude-3-5-sonnet-20241022', 
    label: 'Claude 3.5 Sonnet', 
    provider: 'Anthropic',
    description: 'Anthropic\'s latest model'
  },
  { 
    value: 'gemini-pro', 
    label: 'Gemini Pro', 
    provider: 'Google',
    description: 'Google\'s advanced model'
  },
];

export function LegalQuestionForm({ onSubmit, isLoading }: LegalQuestionFormProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    watch,
    setValue,
    reset
  } = useForm<LegalQuestionFormData>({
    resolver: zodResolver(legalQuestionSchema),
    defaultValues: {
      jurisdiction: 'US',
      practice_area: 'general',
      models: ['gpt-4-turbo-preview', 'claude-3-5-sonnet-20241022', 'gemini-pro'],
      include_comparison: true,
    },
    mode: 'onChange',
  });

  const watchedQuestion = watch('question');
  const watchedModels = watch('models') || [];

  const handleFormSubmit = async (data: LegalQuestionFormData) => {
    const request: LegalQuestionRequest = {
      question: data.question.trim(),
      jurisdiction: data.jurisdiction as any,
      practice_area: data.practice_area as any,
      context: data.context?.trim() || undefined,
      models: data.models && data.models.length > 0 ? data.models : undefined,
      include_comparison: data.include_comparison,
    };

    await onSubmit(request);
  };

  const handleModelToggle = (modelValue: string) => {
    const currentModels = watchedModels;
    const newModels = currentModels.includes(modelValue)
      ? currentModels.filter(m => m !== modelValue)
      : [...currentModels, modelValue];
    
    setValue('models', newModels);
  };

  const characterCount = watchedQuestion?.length || 0;
  const isOverLimit = characterCount > 2000;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-sm border p-6"
    >
      <div className="flex items-center space-x-3 mb-6">
        <div className="flex items-center justify-center w-10 h-10 bg-indigo-600 rounded-lg">
          <FileText className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Ask a Legal Question</h2>
          <p className="text-sm text-gray-500">Get comprehensive analysis from multiple AI models</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
        {/* Question Input */}
        <div>
          <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
            Legal Question *
          </label>
          <textarea
            id="question"
            {...register('question')}
            rows={4}
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors ${
              errors.question ? 'border-red-300' : 'border-gray-300'
            } ${isOverLimit ? 'border-red-300' : ''}`}
            placeholder="Enter your legal question here. Be as specific as possible for better results..."
            disabled={isLoading}
          />
          <div className="flex justify-between items-center mt-1">
            {errors.question ? (
              <p className="text-sm text-red-600 flex items-center space-x-1">
                <AlertCircle className="w-4 h-4" />
                <span>{errors.question.message}</span>
              </p>
            ) : (
              <p className="text-sm text-gray-500">
                Provide context, specific facts, and the legal issue you need help with
              </p>
            )}
            <span className={`text-sm ${isOverLimit ? 'text-red-600' : 'text-gray-500'}`}>
              {characterCount}/2000
            </span>
          </div>
        </div>

        {/* Jurisdiction and Practice Area */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="jurisdiction" className="block text-sm font-medium text-gray-700 mb-2">
              <Globe className="w-4 h-4 inline mr-1" />
              Jurisdiction *
            </label>
            <select
              id="jurisdiction"
              {...register('jurisdiction')}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
              disabled={isLoading}
            >
              {jurisdictions.map((jurisdiction) => (
                <option key={jurisdiction.value} value={jurisdiction.value}>
                  {jurisdiction.flag} {jurisdiction.label}
                </option>
              ))}
            </select>
            {errors.jurisdiction && (
              <p className="text-sm text-red-600 mt-1">{errors.jurisdiction.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="practice_area" className="block text-sm font-medium text-gray-700 mb-2">
              <Briefcase className="w-4 h-4 inline mr-1" />
              Practice Area *
            </label>
            <select
              id="practice_area"
              {...register('practice_area')}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
              disabled={isLoading}
            >
              {practiceAreas.map((area) => (
                <option key={area.value} value={area.value}>
                  {area.icon} {area.label}
                </option>
              ))}
            </select>
            {errors.practice_area && (
              <p className="text-sm text-red-600 mt-1">{errors.practice_area.message}</p>
            )}
          </div>
        </div>

        {/* Context Input */}
        <div>
          <label htmlFor="context" className="block text-sm font-medium text-gray-700 mb-2">
            Additional Context (Optional)
          </label>
          <textarea
            id="context"
            {...register('context')}
            rows={2}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
            placeholder="Provide any additional context, background information, or specific circumstances..."
            disabled={isLoading}
          />
          {errors.context && (
            <p className="text-sm text-red-600 mt-1">{errors.context.message}</p>
          )}
        </div>

        {/* Advanced Options */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center space-x-2 text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
          >
            <span>Advanced Options</span>
            <motion.div
              animate={{ rotate: showAdvanced ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </motion.div>
          </button>

          <motion.div
            initial={false}
            animate={{ height: showAdvanced ? 'auto' : 0, opacity: showAdvanced ? 1 : 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="mt-4 space-y-4 pt-4 border-t border-gray-200">
              {/* Model Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Select AI Models
                </label>
                <div className="space-y-2">
                  {availableModels.map((model) => (
                    <label key={model.value} className="flex items-start space-x-3">
                      <input
                        type="checkbox"
                        checked={watchedModels.includes(model.value)}
                        onChange={() => handleModelToggle(model.value)}
                        className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                        disabled={isLoading}
                      />
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-900">{model.label}</span>
                          <span className="text-xs text-gray-500">({model.provider})</span>
                        </div>
                        <p className="text-xs text-gray-600">{model.description}</p>
                      </div>
                    </label>
                  ))}
                </div>
                {watchedModels.length === 0 && (
                  <p className="text-sm text-amber-600 mt-2 flex items-center space-x-1">
                    <AlertCircle className="w-4 h-4" />
                    <span>Please select at least one model</span>
                  </p>
                )}
              </div>

              {/* Comparison Toggle */}
              <div>
                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    {...register('include_comparison')}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    disabled={isLoading}
                  />
                  <div>
                    <span className="text-sm font-medium text-gray-900">Include Response Comparison</span>
                    <p className="text-xs text-gray-600">Compare and analyze responses from different models</p>
                  </div>
                </label>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isLoading || !isValid || watchedModels.length === 0}
            className="inline-flex items-center space-x-2 px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Ask Legal Question</span>
              </>
            )}
          </button>
        </div>

        {/* Form Validation Summary */}
        {!isValid && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <div className="flex items-start space-x-2">
              <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5" />
              <div>
                <h4 className="text-sm font-medium text-amber-800">Please fix the following issues:</h4>
                <ul className="text-sm text-amber-700 mt-1 space-y-1">
                  {errors.question && <li>• {errors.question.message}</li>}
                  {errors.jurisdiction && <li>• {errors.jurisdiction.message}</li>}
                  {errors.practice_area && <li>• {errors.practice_area.message}</li>}
                  {errors.context && <li>• {errors.context.message}</li>}
                  {watchedModels.length === 0 && <li>• Please select at least one AI model</li>}
                </ul>
              </div>
            </div>
          </div>
        )}
      </form>
    </motion.div>
  );
}
