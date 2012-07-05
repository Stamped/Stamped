//
//  STNewNavigationBar.h
//  Stamped
//
//  Created by Landon Judkins on 7/1/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STBlockUIView.h"
#import "STUser.h"

@interface STNewNavigationBar : UINavigationBar{
    STBlockUIView *_userStrip;
}

@property (nonatomic, assign) BOOL hideLogo;
@property (nonatomic, copy) NSString* string;

- (void)showUserStrip:(BOOL)show forUser:(id<STUser>)user;

@end
