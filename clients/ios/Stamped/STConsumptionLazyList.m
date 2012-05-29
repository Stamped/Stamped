//
//  STConsumptionLazyList.m
//  Stamped
//
//  Created by Landon Judkins on 4/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STConsumptionLazyList.h"
#import "STStampedAPI.h"

@implementation STConsumptionLazyList

@synthesize scope = _scope;
@synthesize section = _section;
@synthesize subsection = _subsection;

- (id)initWithScope:(STStampedAPIScope)scope
            section:(NSString*)section 
         subsection:(NSString*)subsection {
    self = [super init];
    if (self) {
        _scope = scope;
        _section = [section copy];
        _subsection = [subsection copy];
    }
    return self;
}

- (void)dealloc
{
    [_section release];
    [_subsection release];
    [super dealloc];
}

- (STCancellation*)fetchWithRange:(NSRange)range
                      andCallback:(void (^)(NSArray* results, NSError* error, STCancellation* cancellation))block {
    return [[STStampedAPI sharedInstance] entitiesWithScope:self.scope
                                                    section:self.section
                                                 subsection:self.subsection
                                                      limit:[NSNumber numberWithInteger:range.length]
                                                     offset:[NSNumber numberWithInteger:range.location]
                                                andCallback:^(NSArray<STEntityDetail> *entities, NSError *error, STCancellation *cancellation) {
                                                    block((id)entities, error, cancellation); 
                                                }];
    
}

@end
