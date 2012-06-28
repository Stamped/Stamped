//
//  STPlayerPopUp.h
//  Stamped
//
//  Created by Landon Judkins on 6/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STPlayerPopUp : UIView

+ (void)present;

+ (void)presentWithItems:(NSArray<STPlaylistItem>*)playlist clear:(BOOL)clear;

@end
