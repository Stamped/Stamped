//
//  STTodoButton.m
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STTodoButton.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "Util.h"
#import "STStampedAPI.h"
#import "STSharedCaches.h"

@interface STTodoButton ()

@property (nonatomic, readwrite, assign) BOOL waiting;

@property (nonatomic, readonly, retain) NSString* entityID;

@end

@implementation STTodoButton

@synthesize entityID = _entityID;
@synthesize waiting = waiting_;

- (id)initWithStamp:(id<STStamp>)stamp andEntityID:(NSString*)entityID
{
    self = [super initWithStamp:stamp normalOffImage:[UIImage imageNamed:@"sDetailBar_btn_todo"] offText:@"To-Do" andOnText:@"To-Do'd"];
    if (self) {
        
        self.normalOnImage = [UIImage imageNamed:@"sDetailBar_btn_todo_selected"];
        self.touchedOffImage = [UIImage imageNamed:@"sDetailBar_btn_todo_active"];
        self.touchedOnImage = [UIImage imageNamed:@"sDetailBar_btn_todo_active"];
        if (stamp.isTodod.boolValue) {
            self.on = YES;
        }
        else {
            STCache* todos = [STSharedCaches cacheForTodos];
            if (todos) {
                STCacheSnapshot* snapshot = todos.snapshot;
                if ([snapshot.page indexForKey:entityID]) {
                    self.on = YES;
                }
            }
        }
        _entityID = [entityID retain];
    }
    return self;
}

- (id)initWithEntityID:(NSString*)entityID {
    return [self initWithStamp:nil andEntityID:entityID];
}

- (id)initWithStamp:(id<STStamp>)stamp {
    return [self initWithStamp:stamp andEntityID:nil];
}

- (void)dealloc
{
    [_entityID release];
    [super dealloc];
}

- (void)defaultHandler:(id)myself {
    if (!self.waiting) {
        self.waiting = YES;
        if (self.stamp) {
            STActionContext* context = [STActionContext contextWithCompletionBlock:^(id stamp, NSError* error) {
                self.waiting = NO;
                if (!error) {
                    //[Util reloadStampedData];
                }
                else {
                    self.on = !self.on;
                    [Util warnWithMessage:@"Todo failed; see log" andBlock:nil];
                }
            }];
            context.stamp = self.stamp;
            id<STAction> action;
            if (self.stamp.isTodod.boolValue) {
                action = [STStampedActions actionUntodoStamp:self.stamp.stampID withOutputContext:context];
            }
            else {
                action = [STStampedActions actionTodoStamp:self.stamp.stampID withOutputContext:context];
            }
            [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
            self.on = !self.on;
        }
        else {
            BOOL current = self.on;
            [[STStampedAPI sharedInstance] todoWithStampID:nil entityID:self.entityID andCallback:^(id<STTodo> todo, NSError* error, STCancellation* cancellation) {
                self.waiting = NO;
                if (!todo) {
                    self.on = current;
                    [Util warnWithMessage:@"Todo failed; see log" andBlock:nil];
                }
            }];
            self.on = !current;
        }
    }
}

- (void)setStamp:(id<STStamp>)stamp {
    [super setStamp:stamp];
    self.on = stamp.isTodod.boolValue;
}

@end
