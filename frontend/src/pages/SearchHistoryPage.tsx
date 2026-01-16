import React, { useEffect, useState } from 'react';
import { SearchForm } from '../components/SearchForm';
import { Clock, TrendingUp } from 'lucide-react';
import axios from 'axios';

interface SearchQuery {
  id: number;
  search_query: string;
  sources: string[];
  status: string;
  created_at: string;
  total_found: number;
}

export const SearchHistoryPage: React.FC = () => {
  const [history, setHistory] = useState<SearchQuery[]>([]);
  const [loading, setLoading] = useState(true);

  const loadHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/api/search/queries`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      setHistory(response.data.queries);
    } catch (error) {
      console.error('Ошибка загрузки истории:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleSearchComplete = () => {
    // Обновляем историю после нового поиска
    setTimeout(() => loadHistory(), 1000);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Форма поиска */}
        <div>
          <SearchForm onSearchComplete={handleSearchComplete} />
        </div>

        {/* История поисков */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            <Clock className="mr-2" />
            История поисков
          </h2>

          {loading ? (
            <div className="text-center py-8">Загрузка...</div>
          ) : history.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>Вы еще не делали поисков</p>
              <p className="text-sm mt-2">Начните с формы слева 👈</p>
            </div>
          ) : (
            <div className="space-y-4">
              {history.map((query) => (
                <div
                  key={query.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => window.location.href = `/results?query=${encodeURIComponent(query.search_query)}`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">
                        {query.search_query}
                      </h3>
                      <p className="text-sm text-gray-500 mt-1">
                        {new Date(query.created_at).toLocaleString('ru-RU')}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className={`
                        px-2 py-1 rounded text-xs font-semibold
                        ${query.status === 'completed' ? 'bg-green-100 text-green-800' : ''}
                        ${query.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : ''}
                        ${query.status === 'error' ? 'bg-red-100 text-red-800' : ''}
                      `}>
                        {query.status}
                      </span>
                    </div>
                  </div>

                  <div className="mt-3 flex items-center gap-4 text-sm text-gray-600">
                    <span>
                      Источники: {query.sources.join(', ')}
                    </span>
                    {query.total_found > 0 && (
                      <span className="flex items-center">
                        <TrendingUp size={16} className="mr-1" />
                        Найдено: {query.total_found}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};