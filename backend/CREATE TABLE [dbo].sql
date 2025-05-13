CREATE TABLE [dbo].[Messages] (
    [message_id]   INT            IDENTITY (1, 1) NOT NULL,
    [user_id]      INT            NOT NULL,
    [message_text] NVARCHAR (MAX) NOT NULL,
    [probability]  FLOAT    NOT NULL,
    CONSTRAINT [PK_Messages] PRIMARY KEY CLUSTERED ([message_id] ASC),
    CONSTRAINT [user_id] FOREIGN KEY ([user_id]) REFERENCES [dbo].[Users] ([user_id])
);

