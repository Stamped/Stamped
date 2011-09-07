//
//  UserImageView.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/12/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class User;

@interface UserImageView : UIControl
@property (nonatomic, readonly) UIImageView* imageView;
@property (nonatomic, copy) NSString* imageURL;
@end
