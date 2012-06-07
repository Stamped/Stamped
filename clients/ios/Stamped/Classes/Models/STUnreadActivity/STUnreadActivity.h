//
//  STUnreadActivity.h
//  Stamped
//
//  Created by Devin Doty on 6/6/12.
//
//

#import <Foundation/Foundation.h>

@interface STUnreadActivity : NSObject {
    BOOL _updating;
}
+ (id)sharedInstance ;
- (void)update;

@end
