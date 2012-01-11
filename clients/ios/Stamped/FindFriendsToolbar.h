//
//  FindFriendsToolbar.h
//  Stamped
//
//  Created by Andrew Bonventre on 1/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STToolbar.h"

@class FindFriendsToolbar;

@protocol FindFriendsToolbarDelegate
@required
- (void)toolbar:(FindFriendsToolbar*)toolbar centerButtonPressed:(UIButton*)button;
@end

@interface FindFriendsToolbar : STToolbar

@property (nonatomic, readonly) UIButton* previewButton;
@property (nonatomic, readonly) UIButton* mainActionButton;
@property (nonatomic, readonly) UIButton* addEmailsButton;
@property (nonatomic, readonly) UIButton* centerButton;

@property (nonatomic, assign) id<FindFriendsToolbarDelegate> delegate;

@end
