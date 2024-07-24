USE [NombreDB]
GO
/****** Object:  Table [dbo].[area]    Script Date: 23/07/2024 13:00:54 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[area](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[nombre] [varchar](100) NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[asignacion_equipo]    Script Date: 23/07/2024 13:00:54 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[asignacion_equipo](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[equipo_id] [int] NOT NULL,
	[persona_id] [int] NOT NULL,
	[fecha_asignacion] [datetime] NOT NULL,
	[fecha_devolucion] [datetime] NULL,
	[observaciones] [text] NULL,
	[archivo_pdf] [nvarchar](255) NULL,
	[archivo_pdf_devolucion] [varchar](255) NULL,
PRIMARY KEY CLUSTERED
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[celular]    Script Date: 23/07/2024 13:00:54 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[celular](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[nombre] [varchar](100) NULL,
	[marca] [varchar](100) NULL,
	[modelo] [varchar](100) NULL,
	[serial] [varchar](100) NULL,
	[imei1] [varchar](100) NULL,
	[imei2] [varchar](100) NULL,
	[ntelefono] [varchar](100) NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[equipo]    Script Date: 23/07/2024 13:00:54 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[equipo](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[estadoequipo_id] [int] NULL,
	[unidad_id] [int] NULL,
	[celular_id] [int] NULL,
	[tipoequipo_id] [int] NULL,
	[observaciones] [varchar](255) NULL,
	[fcreacion] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[estadoequipo]    Script Date: 23/07/2024 13:00:54 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[estadoequipo](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[nombre] [varchar](100) NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[persona]    Script Date: 23/07/2024 13:00:54 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[persona](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[nombres] [varchar](100) NULL,
	[apellidos] [varchar](100) NULL,
	[correo] [varchar](100) NULL,
	[rut] [varchar](20) NULL,
	[dv] [char](1) NULL,
	[area_id] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[tipoequipo]    Script Date: 23/07/2024 13:00:54 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[tipoequipo](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[nombre] [varchar](100) NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[unidad]    Script Date: 23/07/2024 13:00:54 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[unidad](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[nombre_e] [varchar](100) NULL,
	[marca] [varchar](100) NULL,
	[modelo] [varchar](100) NULL,
	[ram] [int] NULL,
	[procesador] [varchar](100) NULL,
	[almc] [varchar](100) NULL,
	[perif] [varchar](100) NULL,
	[numsello] [varchar](100) NULL,
	[serial] [varchar](100) NULL,
	[numproducto] [varchar](100) NULL,
	[tipoimpresion] [varchar](100) NULL,
	[cantidad] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[Usuarios]    Script Date: 23/07/2024 13:00:54 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[Usuarios](
	[usuarios_id] [int] IDENTITY(1,1) NOT NULL,
	[usuarios_nombre] [varchar](50) NULL,
	[usuarios_ap_paterno] [varchar](50) NULL,
	[usuarios_ap_materno] [varchar](50) NULL,
	[usuarios_correo] [varchar](50) NULL,
	[usuarios_contraseña] [varchar](512) NULL,
	[usuarios_rut] [varchar](50) NULL,
 CONSTRAINT [PK_Usuarios] PRIMARY KEY CLUSTERED 
(
	[usuarios_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
ALTER TABLE [dbo].[asignacion_equipo]  WITH CHECK ADD  CONSTRAINT [FK_asignacion_equipo_equipo] FOREIGN KEY([equipo_id])
REFERENCES [dbo].[equipo] ([id])
GO
ALTER TABLE [dbo].[asignacion_equipo] CHECK CONSTRAINT [FK_asignacion_equipo_equipo]
GO
ALTER TABLE [dbo].[asignacion_equipo]  WITH CHECK ADD  CONSTRAINT [FK_persona] FOREIGN KEY([persona_id])
REFERENCES [dbo].[persona] ([id])
ON UPDATE CASCADE
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[asignacion_equipo] CHECK CONSTRAINT [FK_persona]
GO
ALTER TABLE [dbo].[equipo]  WITH CHECK ADD  CONSTRAINT [FK_equipo_celular] FOREIGN KEY([celular_id])
REFERENCES [dbo].[celular] ([id])
ON UPDATE CASCADE
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[equipo] CHECK CONSTRAINT [FK_equipo_celular]
GO
ALTER TABLE [dbo].[equipo]  WITH CHECK ADD  CONSTRAINT [FK_equipo_estadoequipo] FOREIGN KEY([estadoequipo_id])
REFERENCES [dbo].[estadoequipo] ([id])
GO
ALTER TABLE [dbo].[equipo] CHECK CONSTRAINT [FK_equipo_estadoequipo]
GO
ALTER TABLE [dbo].[equipo]  WITH CHECK ADD  CONSTRAINT [FK_equipo_tipoequipo] FOREIGN KEY([tipoequipo_id])
REFERENCES [dbo].[tipoequipo] ([id])
GO
ALTER TABLE [dbo].[equipo] CHECK CONSTRAINT [FK_equipo_tipoequipo]
GO
ALTER TABLE [dbo].[equipo]  WITH CHECK ADD  CONSTRAINT [FK_equipo_unidad] FOREIGN KEY([unidad_id])
REFERENCES [dbo].[unidad] ([id])
ON UPDATE CASCADE
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[equipo] CHECK CONSTRAINT [FK_equipo_unidad]
GO
ALTER TABLE [dbo].[persona]  WITH CHECK ADD  CONSTRAINT [FK__persona__area_id__3C69FB99] FOREIGN KEY([area_id])
REFERENCES [dbo].[area] ([id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[persona] CHECK CONSTRAINT [FK__persona__area_id__3C69FB99]
GO
