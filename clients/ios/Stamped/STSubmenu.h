//
//  STSubmenu.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STMenuSection.h"
#import "STTimes.h"

@protocol STSubmenu <NSObject>

@property (nonatomic, readonly, retain) NSString* title;
@property (nonatomic, readonly, retain) NSString* footnote;
@property (nonatomic, readonly, retain) NSString* desc;
@property (nonatomic, readonly, retain) NSString* short_desc;
@property (nonatomic, readonly, retain) NSArray<STTimes>* times;
@property (nonatomic, readonly, retain) NSArray<STMenuSection>* sections;

@end
