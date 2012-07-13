//
//  STStampButton.m
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampButton.h"
#import "Util.h"
#import "CreateStampViewController.h"
#import "STStampedAPI.h"

@interface STStampButton ()

@property (nonatomic, readwrite, retain) id<STUser> user;
@property (nonatomic, readwrite, retain) id<STEntity> entity;

- (id)initWithEntity:(id<STEntity>)entity andUser:(id<STUser>)user;

@end

@implementation STStampButton

@synthesize user = _user;
@synthesize entity = _entity;

- (id)initWithEntity:(id<STEntity>)entity andUser:(id<STUser>)user {
    UIImage* normalImage = [UIImage imageNamed:@"sDetailBar_btn_restamp"];
//    if (user && [user.screenName isEqualToString:[STStampedAPI sharedInstance].currentUser.screenName]) {
//        UIImage* whiteMask = [Util whiteMaskedImageUsingImage:normalImage];
//        normalImage = [Util gradientImage:normalImage withPrimaryColor:user.primaryColor secondary:user.secondaryColor];
//        
//        
//        CGFloat width = normalImage.size.width;
//        CGFloat height = normalImage.size.height;
//        
//        UIGraphicsBeginImageContextWithOptions(normalImage.size, NO, 0.0);
//        CGContextRef context = UIGraphicsGetCurrentContext();
//        
//        CGContextTranslateCTM(context, 0, height);
//        CGContextScaleCTM(context, 1.0, -1.0);
//        CGContextDrawImage(context, CGRectMake(0, 0, width, height), whiteMask.CGImage);
//        CGContextDrawImage(context, CGRectMake(0, 0, width, height), normalImage.CGImage);
//        UIImage* maskedImage = UIGraphicsGetImageFromCurrentImageContext();
//        UIGraphicsEndImageContext();
//        normalImage = maskedImage;
//    }
    self = [super initWithNormalOffImage:normalImage offText:@"Stamp" andOnText:@"Stamped"];
    if (self) {
        self.touchedOffImage = [UIImage imageNamed:@"sDetailBar_btn_restamp_active"];
        self.touchedOnImage= [UIImage imageNamed:@"sDetailBar_btn_restamp_active"];
        self.normalOffImage = [UIImage imageNamed:@"sDetailBar_btn_restamp"];
        _user = [user retain];
        _entity = [entity retain];
    }
    return self;
}

- (id)initWithStamp:(id<STStamp>)stamp {
    return [self initWithEntity:stamp.entity andUser:stamp.user];
}

- (id)initWithEntity:(id<STEntity>)entity {
    return [self initWithEntity:entity andUser:nil];
}

- (void)dealloc {
    [_user release];
    [_entity release];
    [super dealloc];
}

- (void)defaultHandler:(id)myself {
    
    if (self.entity) {
        CreateStampViewController *controller = [[[CreateStampViewController alloc] initWithEntity:self.entity] autorelease];
        [[Util sharedNavigationController] pushViewController:controller animated:YES];
        if (self.user) {
            controller.creditUsers = [NSArray arrayWithObject:self.user];
        }
    }
    
}

@end
