import React, { useState, useEffect } from 'react';
import { Layout, Menu, Typography, Card, Row, Col, Statistic } from 'antd';
import {
  DashboardOutlined,
  BarChartOutlined,
  CloudDownloadOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import apiService from '../services/api';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const [overview, setOverview] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOverview();
  }, []);

  const loadOverview = async () => {
    try {
      const data = await apiService.getAnalyticsOverview();
      setOverview(data);
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const sentimentColors = {
    positive: '#52c41a',
    negative: '#f5222d',
    neutral: '#faad14',
  };

  const sentimentData = overview?.sentiment_distribution?.map((item: any) => ({
    name: item._id === 'positive' ? 'Позитивные' : item._id === 'negative' ? 'Негативные' : 'Нейтральные',
    value: item.count,
    color: sentimentColors[item._id as keyof typeof sentimentColors],
  })) || [];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
        <div style={{
          height: 32,
          margin: 16,
          color: 'white',
          fontSize: 18,
          fontWeight: 'bold',
          textAlign: 'center'
        }}>
          {collapsed ? 'VK' : 'VK Analytics'}
        </div>
        <Menu
          theme="dark"
          defaultSelectedKeys={['1']}
          mode="inline"
          items={[
            {
              key: '1',
              icon: <DashboardOutlined />,
              label: 'Дашборд',
              onClick: () => navigate('/dashboard'),
            },
            {
              key: '2',
              icon: <BarChartOutlined />,
              label: 'Аналитика',
              onClick: () => navigate('/analytics'),
            },
            {
              key: '3',
              icon: <CloudDownloadOutlined />,
              label: 'Сбор данных',
              onClick: () => navigate('/collection'),
            },
            {
              key: '4',
              icon: <LogoutOutlined />,
              label: 'Выход',
              onClick: handleLogout,
            },
          ]}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px' }}>
          <Title level={3} style={{ margin: '16px 0' }}>Дашборд</Title>
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff' }}>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Всего отзывов"
                  value={sentimentData.reduce((acc: number, item: any) => acc + item.value, 0)}
                  valueStyle={{ color: '#3f8600' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Позитивных"
                  value={sentimentData.find((item: any) => item.name === 'Позитивные')?.value || 0}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Негативных"
                  value={sentimentData.find((item: any) => item.name === 'Негативные')?.value || 0}
                  valueStyle={{ color: '#f5222d' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Нейтральных"
                  value={sentimentData.find((item: any) => item.name === 'Нейтральные')?.value || 0}
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
          </Row>

          <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
            <Col xs={24} lg={12}>
              <Card title="Распределение тональности">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={sentimentData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => `${entry.name}: ${entry.value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {sentimentData.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title="Топ ключевых слов" loading={loading}>
                {overview?.top_keywords?.slice(0, 10).map((item: any, index: number) => (
                  <div key={index} style={{
                    padding: '8px 0',
                    borderBottom: '1px solid #f0f0f0',
                    display: 'flex',
                    justifyContent: 'space-between'
                  }}>
                    <span>{item._id}</span>
                    <span style={{ fontWeight: 'bold' }}>{item.count}</span>
                  </div>
                ))}
              </Card>
            </Col>
          </Row>
        </Content>
      </Layout>
    </Layout>
  );
};

export default Dashboard;