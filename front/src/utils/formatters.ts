// 格式化价格显示的通用工具函数
export function formatPrice(price: number | string): string {
  // 确保价格是数字
  const numPrice = Number(price)
  if (isNaN(numPrice)) return '0'
  
  // 如果是整数，不显示小数部分
  if (numPrice % 1 === 0) {
    return numPrice.toString()
  }
  
  // 如果有小数，保留2位小数并去掉尾随的0
  return numPrice.toFixed(2).replace(/\.?0+$/, '')
}

// 格式化货币显示（带货币符号）
export function formatCurrency(price: number | string, symbol: string = '¥'): string {
  return `${symbol}${formatPrice(price)}`
} 