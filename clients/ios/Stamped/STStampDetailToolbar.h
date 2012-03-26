//
//  STStampDetailToolbar.h
//  Stamped
//
//  Created by Andrew Bonventre on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STToolbar.h"

typedef enum {
  STStampDetailToolbarStyleDefault = 0,
  STStampDetailToolbarStyleMine,
} STStampDetailToolbarStyle;

@interface STStampDetailToolbar : STToolbar

@property (nonatomic, assign) STStampDetailToolbarStyle style;

@property (nonatomic, readonly) UIButton* likeButton;
@property (nonatomic, readonly) UIButton* todoButton;
@property (nonatomic, readonly) UIButton* stampButton;
@property (nonatomic, readonly) UIButton* shareButton;

@end
