import React from 'react';
import { Form, Input, Button, Card, message } from 'antd';
import { useNavigate } from 'react-router-dom';

const Register: React.FC = () => {
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    try {
      console.log('Register:', values);
      message.success('Регистрация успешна!');
      navigate('/login');
    } catch (error) {
      message.error('Ошибка регистрации');
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f0f2f5' }}>
      <Card title="Регистрация" style={{ width: 400 }}>
        <Form onFinish={onFinish} layout="vertical">
          <Form.Item
            name="username"
            label="Имя пользователя"
            rules={[{ required: true, message: 'Введите имя пользователя' }]}
          >
            <Input placeholder="Имя пользователя" />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Введите email' },
              { type: 'email', message: 'Введите корректный email' }
            ]}
          >
            <Input placeholder="Email" />
          </Form.Item>

          <Form.Item
            name="password"
            label="Пароль"
            rules={[
              { required: true, message: 'Введите пароль' },
              { min: 6, message: 'Пароль должен быть минимум 6 символов' }
            ]}
          >
            <Input.Password placeholder="Пароль" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Зарегистрироваться
            </Button>
          </Form.Item>

          <Button type="link" onClick={() => navigate('/login')} block>
            Уже есть аккаунт? Войти
          </Button>
        </Form>
      </Card>
    </div>
  );
};

export default Register;