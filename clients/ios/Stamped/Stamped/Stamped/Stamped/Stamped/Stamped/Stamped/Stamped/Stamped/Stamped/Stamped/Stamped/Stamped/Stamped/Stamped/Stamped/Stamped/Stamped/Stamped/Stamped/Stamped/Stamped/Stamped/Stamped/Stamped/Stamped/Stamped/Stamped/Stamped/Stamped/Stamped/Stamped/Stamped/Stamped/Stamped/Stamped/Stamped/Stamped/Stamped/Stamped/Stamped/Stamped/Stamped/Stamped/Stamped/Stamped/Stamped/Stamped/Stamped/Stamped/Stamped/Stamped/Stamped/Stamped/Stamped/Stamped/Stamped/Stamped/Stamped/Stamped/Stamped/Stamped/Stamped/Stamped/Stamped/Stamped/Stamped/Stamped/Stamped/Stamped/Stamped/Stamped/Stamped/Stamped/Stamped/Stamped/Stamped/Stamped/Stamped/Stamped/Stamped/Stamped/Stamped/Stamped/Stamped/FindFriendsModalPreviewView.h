//
//  FindFriendsModalPreviewView.h
//  Stamped
//
//  Created by Andrew Bonventre on 1/17/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class STImageView;

typedef enum {
  FindFriendsModalTypeTwitter,
  FindFriendsModalTypeFacebook,
  FindFriendsModalTypeEmail
} FindFriendsModalType;

@interface FindFriendsModalPreviewView : UIView

@property (nonatomic, readonly) UILabel* titleLabel;
@property (nonatomic, assign) FindFriendsModalType modalType;
@property (nonatomic, assign) NSUInteger numInvites;
@property (nonatomic, readonly) STImageView* profileImageView;
@property (nonatomic, readonly) UILabel* headerLabel;
@property (nonatomic, readonly) UILabel* mainTextLabel;
@property (nonatomic, copy) NSString* sampleTwitterUsername;

@end
