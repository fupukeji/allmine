import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { TabBar } from 'antd-mobile'
import { 
  AppOutline,
  BillOutline,
  FileOutline,
  UserOutline
} from 'antd-mobile-icons'
import './MobileLayout.css'

const MobileLayout = ({ onLogout }) => {
  const navigate = useNavigate()
  const location = useLocation()

  const tabs = [
    {
      key: '/',
      title: '首页',
      icon: <AppOutline />
    },
    {
      key: '/virtual-assets',
      title: '随风而逝',
      icon: <BillOutline />
    },
    {
      key: '/fixed-assets',
      title: '恒产生金',
      icon: <FileOutline />
    },
    {
      key: '/profile',
      title: '我的',
      icon: <UserOutline />
    }
  ]

  const setRouteActive = (value) => {
    navigate(value)
  }

  return (
    <div className="mobile-layout">
      <div className="mobile-content">
        <Outlet />
      </div>
      
      <div className="mobile-tabbar">
        <TabBar activeKey={location.pathname} onChange={setRouteActive}>
          {tabs.map(item => (
            <TabBar.Item key={item.key} icon={item.icon} title={item.title} />
          ))}
        </TabBar>
      </div>
    </div>
  )
}

export default MobileLayout
