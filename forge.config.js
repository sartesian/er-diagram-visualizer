module.exports = {
  packagerConfig: {},
  makers: [
    {
      name: '@electron-forge/maker-squirrel',
      config: {
        name: 'er_diagram_visualizer',
        authors: 'ornstein', // Укажите ваше имя или название компании
        description: 'A database visualizer tool for ER diagrams' // Описание приложения
      }
    }
  ]
};