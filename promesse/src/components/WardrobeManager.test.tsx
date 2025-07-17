import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import WardrobeManager from './WardrobeManager';
import { Toaster } from '@/components/ui/toaster';
import { AuthProvider } from '@/contexts/AuthContext';

const server = setupServer(
  rest.get('/api/wardrobe/wardrobe-items', (req, res, ctx) => {
    return res(ctx.json([]));
  }),
  rest.post('/api/wardrobe/wardrobe-items', (req, res, ctx) => {
    return res(ctx.json({ id: 1, name: 'Test Item' }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('WardrobeManager', () => {
  it('renders the component', async () => {
    render(
      <AuthProvider>
        <WardrobeManager />
        <Toaster />
      </AuthProvider>
    );

    expect(screen.getByText('My Wardrobe')).toBeInTheDocument();
  });

  it('fetches and displays wardrobe items', async () => {
    server.use(
      rest.get('/api/wardrobe/wardrobe-items', (req, res, ctx) => {
        return res(
          ctx.json([
            { id: 1, name: 'Test Item 1', brand: 'Test Brand 1', category: 'Tops', times_worn: 1 },
            { id: 2, name: 'Test Item 2', brand: 'Test Brand 2', category: 'Bottoms', times_worn: 2 },
          ])
        );
      })
    );

    render(
      <AuthProvider>
        <WardrobeManager />
        <Toaster />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Test Item 1')).toBeInTheDocument();
      expect(screen.getByText('Test Item 2')).toBeInTheDocument();
    });
  });

  it('opens the add item modal', async () => {
    render(
      <AuthProvider>
        <WardrobeManager />
        <Toaster />
      </AuthProvider>
    );

    fireEvent.click(screen.getByText('Add Item'));

    await waitFor(() => {
      expect(screen.getByText('Add New Wardrobe Item')).toBeInTheDocument();
    });
  });
});
