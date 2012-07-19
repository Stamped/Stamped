//
//  STNavigationBar.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STBlockUIView.h"
#import "STUser.h"

@interface STNavigationBar : UINavigationBar {
    STBlockUIView *_userStrip;
}

@property (nonatomic, assign) BOOL black;
@property (nonatomic, assign) BOOL hideLogo;
@property (nonatomic, copy) NSString* string;
@property (nonatomic, readwrite, copy) NSString* title;

- (void)showUserStrip:(BOOL)show forUser:(id<STUser>)user;

@end
