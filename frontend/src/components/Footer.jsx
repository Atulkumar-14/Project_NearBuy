import React from 'react'
import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="mt-10">
      <div className="rounded-2xl bg-white text-gray-900 p-6 shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div>
            <div className="text-lg font-semibold">Quick Links</div>
            <ul className="mt-2 space-y-1 text-sm">
              <li><Link to="/shops/register" className="hover:underline">Shop Registration</Link></li>
              <li><Link to="/signup" className="hover:underline">Sign Up</Link></li>
              <li><Link to="/user/profile" className="hover:underline">User Profile</Link></li>
              <li><Link to="/shopkeeper/profile" className="hover:underline">Shopkeeper Profile</Link></li>
              <li><Link to="/shops" className="hover:underline">Nearby Shops</Link></li>
              <li><Link to="/products" className="hover:underline">Browse Products</Link></li>
            </ul>
          </div>
          <div>
            <div className="text-lg font-semibold">Support</div>
            <ul className="mt-2 space-y-1 text-sm">
              <li><a href="mailto:support@nearbuy.local" className="hover:underline">Contact</a></li>
              <li><Link to="/admin" className="hover:underline">Admin</Link></li>
              <li><a href="#" className="hover:underline" onClick={(e)=>{e.preventDefault(); window.scrollTo({top:0, behavior:'smooth'})}}>Back to top</a></li>
            </ul>
          </div>
          <div>
            <div className="text-lg font-semibold">Address</div>
            <div className="mt-2 text-sm text-gray-700">Arera Hills, Bhopal, MP 462011</div>
            <div className="text-sm text-gray-700">MP Nagar Zone 1, Bhopal</div>
          </div>
          <div>
            <div className="text-lg font-semibold">About</div>
            <div className="mt-2 text-sm text-gray-700">Compare local shop prices, view nearby availability, and register your shop to reach nearby customers.</div>
          </div>
        </div>
      </div>
      <div className="mt-2 text-xs text-white/80">© {new Date().getFullYear()} NearBuy — All rights reserved.</div>
    </footer>
  )
}