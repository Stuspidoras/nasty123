import React, { useState } from 'react';
import { Search, Loader } from 'lucide-react';
import axios from 'axios';

interface SearchFormProps {
  onSearchComplete?: (queryId: number) => void;
}

export const SearchForm: React.FC<SearchFormProps> = ({ onSearchComplete }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sources, setSources] = useState<string[]>(['vk', 'ok']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (searchQuery.trim().length < 3) {
      setError('Введите минимум 3 символа');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/search/create`,
        {
          search_query: searchQuery,
          sources: sources,
          count: 100
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      setSuccess(`Поиск запущен! Собираем отзывы о "${searchQuery}"...`);

      if (onSearchComplete && response.data.query_id) {
        onSearchComplete(response.data.query_id);
      }

      // Очищаем форму через 2 секунды
      setTimeout(() => {
        setSearchQuery('');
        setSuccess('');
      }, 2000);

    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка при запуске поиска');
    } finally {
      setLoading(false);
    }
  };

  const toggleSource = (source: string) => {
    setSources(prev =>
      prev.includes(source)
        ? prev.filter(s => s !== source)
        : [...prev, source]
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4 flex items-center">
        <Search className="mr-2" />
        Новый поиск отзывов
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Поле поиска */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Что ищем? (например: "телефон самсунг", "ноутбук asus")
          </label>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Введите запрос для поиска..."
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
        </div>

        {/* Выбор источников */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Источники данных:
          </label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={sources.includes('vk')}
                onChange={() => toggleSource('vk')}
                className="mr-2"
                disabled={loading}
              />
              ВКонтакте
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={sources.includes('ok')}
                onChange={() => toggleSource('ok')}
                className="mr-2"
                disabled={loading}
              />
              Одноклассники
            </label>
          </div>
        </div>

        {/* Сообщения */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
            {success}
          </div>
        )}

        {/* Кнопка */}
        <button
          type="submit"
          disabled={loading || sources.length === 0}
          className="w-full bg-blue-600 text-white py-3 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {loading ? (
            <>
              <Loader className="animate-spin mr-2" size={20} />
              Поиск запущен...
            </>
          ) : (
            <>
              <Search className="mr-2" size={20} />
              Начать поиск
            </>
          )}
        </button>
      </form>

      <div className="mt-4 text-sm text-gray-600">
        <p>💡 Примеры запросов:</p>
        <ul className="list-disc list-inside mt-2 space-y-1">
          <li>"iPhone 15 Pro"</li>
          <li>"Наушники Sony"</li>
          <li>"Кофеварка Delonghi"</li>
          <li>"Пылесос Dyson"</li>
        </ul>
      </div>
    </div>
  );
};