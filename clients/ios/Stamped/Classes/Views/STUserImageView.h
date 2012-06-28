//
//  STUserImageView.h
//  Stamped
//
//  Created by Landon Judkins on 6/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STUserImageView : UIImageView

- (id)initWithSize:(CGFloat)size;

- (id)initWithUser:(id<STUser>)user withSize:(CGFloat)size;

- (void)setAction:(id<STAction>)action withContext:(STActionContext*)context;

- (void)clearAction;

- (void)setupWithUser:(id<STUser>)user viewAction:(BOOL)action;

@end
