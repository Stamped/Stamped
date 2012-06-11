//
//  STUnreadActivity.h
//  Stamped
//
//  Created by Devin Doty on 6/6/12.
//
//

#import <Foundation/Foundation.h>

@interface STUnreadActivity : NSObject

+ (STUnreadActivity*)sharedInstance ;
- (void)update;

@property (nonatomic, readwrite, assign) NSInteger count;

@end
