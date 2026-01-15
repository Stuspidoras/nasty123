import React from 'react';
import { Card, Row, Col, Statistic, Table } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { LikeOutlined, DislikeOutlined, MessageOutlined } from '@ant-design/icons';

const Analytics: React.FC = () => {
  // Временные данные для графика
  const chartData = [
    { date: '01.01', positive: 45, negative: 12, neutral: 30 },
    { date: '02.01', positive: 52, negative: 10, neutral: 25 },
    { date: '03.01', positive: 48, negative: 15, neutral: 28 },
    { date: '04.01', positive: 60, negative: 8, neutral: 22 },
    { date: '05.01', positive: 55, negative: 11, neutral: 26 },
  ];

  // Временные данные для таблицы
  const tableData = [
    { key: '1', source: 'ВКонтакте', total: 150, positive: 120, negative: 20, neutral: 10 },
    { key: '2', source: 'Одноклассники', total: 85, positive: 65, negative: 10, neutral: 10 },
  ];

  const columns = [
    { title: 'Источник', dataIndex: 'source', key: 'source' },
    { title: 'Всего', dataIndex: 'total', key: 'total' },
    { title: 'Позитивных', dataIndex: 'positive', key: 'positive' },
    { title: 'Негативных', dataIndex: 'negative', key: 'negative' },
    { title: 'Нейтральных', dataIndex: 'neutral', key: 'neutral' },
  ];

  return (
    <div style={{ padding: 24 }}>
      <h1>Аналитика отзывов</h1>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="Позитивных отзывов"
              value={185}
              prefix={<LikeOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Негативных отзывов"
              value={30}
              prefix={<DislikeOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Всего отзывов"
              value={235}
              prefix={<MessageOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Динамика отзывов" style={{ marginBottom: 24 }}>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="positive" stroke="#52c41a" name="Позитивные" />
            <Line type="monotone" dataKey="negative" stroke="#ff4d4f" name="Негативные" />
            <Line type="monotone" dataKey="neutral" stroke="#1890ff" name="Нейтральные" />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      <Card title="Статистика по источникам">
        <Table dataSource={tableData} columns={columns} pagination={false} />
      </Card>
    </div>
  );
};

export default Analytics;