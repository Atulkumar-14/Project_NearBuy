import React, { useEffect, useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import Nav from './components/Nav'
import ErrorBoundary from './components/ErrorBoundary'
import Footer from './components/Footer'
import Home from './pages/Home'
import Shop from './pages/Shop'
import Shops from './pages/Shops'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Product from './pages/Product'
import Admin from './pages/Admin'
import ShopProduct from './pages/ShopProduct'
import ShopRegister from './pages/ShopRegister'
import ShopManage from './pages/ShopManage'
import ShopAddProduct from './pages/ShopAddProduct'
import ShopAddProductLanding from './pages/ShopAddProductLanding'
import OwnerLogin from './pages/OwnerLogin'
import { RequireOwnerAuth, RequireUserAuth } from './routes/guards'
import ShopkeeperDashboard from './modules/shopkeeper/Dashboard'
import OwnerProducts from './modules/shopkeeper/OwnerProducts'
import ShopkeeperProfile from './modules/shopkeeper/Profile'
import UserDashboard from './modules/user/Dashboard'
import UserProfile from './modules/user/Profile'
import UserSettings from './pages/UserSettings'

export default function App() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Nav />
      <div className="p-4">
        <ErrorBoundary>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Home defaultType="product" />} />
          <Route path="/shops" element={<Shops />} />
          <Route path="/shops/add-product" element={<ShopAddProductLanding />} />
          <Route path="/owner/login" element={<OwnerLogin />} />
          <Route path="/shopkeeper/products" element={<RequireOwnerAuth><OwnerProducts /></RequireOwnerAuth>} />
          <Route path="/shopkeeper/dashboard" element={<RequireOwnerAuth><ShopkeeperDashboard /></RequireOwnerAuth>} />
          <Route path="/shopkeeper/profile" element={<RequireOwnerAuth><ShopkeeperProfile /></RequireOwnerAuth>} />
          <Route path="/shops/register" element={<ShopRegister />} />
          <Route path="/shops/:shopId" element={<Shop />} />
          <Route path="/shops/:shopId/manage" element={<RequireOwnerAuth><ShopManage /></RequireOwnerAuth>} />
          <Route path="/shops/:shopId/add-product" element={<RequireOwnerAuth><ShopAddProduct /></RequireOwnerAuth>} />
          <Route path="/products/:productId" element={<Product />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/shops/:shopId/products/:productId" element={<ShopProduct />} />
          <Route path="/user/dashboard" element={<RequireUserAuth><UserDashboard /></RequireUserAuth>} />
          <Route path="/user/profile" element={<RequireUserAuth><UserProfile /></RequireUserAuth>} />
          <Route path="/user/settings" element={<RequireUserAuth><UserSettings /></RequireUserAuth>} />
        </Routes>
        </ErrorBoundary>
        <Footer />
      </div>
    </div>
  )
}
